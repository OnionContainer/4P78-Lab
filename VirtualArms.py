import sympy
import sympy.vector
from sympy.geometry import Point2D as Point
import cv2
from typing import List, Tuple, Callable, Optional, Any
from datetime import datetime
import time
from ArmMission import ArmMission, RegRotateMission, SegmentMovementMission


class VirtualArms:

    def sync_real(self, m0:int, m1:int):
        self.__motorDegrees[0] = m0
        self.__motorDegrees[1] = m1

    def get_motor_interval(self, motor:int)->sympy.Interval:
        return self.__motorInterval[motor]

    def get_bar_length(self, motor:int)->float:
        return self.__barLength[motor]

    def get_motor_angle(self, motor:int)->float:
        return self.__motorDegrees[motor]

    def has_mission(self)->bool:
        return len(self.__updateFunction) > 0

    def get_current_mission(self)->ArmMission:
        return self.__updateFunction[0]

    def preempt_mission(self, mission:ArmMission):
        self.__updateFunction.insert(0,mission)

    def __init__(self):

        self.a_random_callback = None

        self.__root: Point = Point()
        self.__motorDegrees: List[float] = [-10.0, -115.0]
        self.__motorInterval: List[sympy.Interval] = [
            sympy.Interval(-10, 160),
            sympy.Interval(-115, 110)
        ]
        self.__barLength: List[float] = [105, 133]
        self.__motorSpeed: List[float] = [30, 30]
        self.__noCrossPoints: List[Point] = []  # those are no crossing points
        self.__lastUpdateTime: datetime = datetime.now()

        # self.__updateFunction: Optional[
        #     Callable[[float], bool]] = None  # return true when registered action is complete
        #make it a list to spin different motors at the same time

        self.__updateFunction:List[ArmMission] = []
        #this is a list of executable functions that accepts delta time and returns bool

        print(self.__root)

    def solve_angle_final(self, motor:int)->float:
        if motor == 0:
            return self.__motorDegrees[0]
        else:
            return self.__motorDegrees[motor] + self.solve_angle_final(motor-1)
        pass

    def solve_node_pos(self, node: int) -> tuple[float, float]:
        """
        Calculate the position of the specified node recursively:
        - 0: Return the root point.
        - 1: Return the position of the first motor.
        - 2: Return the position of the second bar's tip.

        Contributed by ChatGPT.
        """
        if node == 0:
            return self.__root.x, self.__root.y
        elif node > 0:
            prev_point = self.solve_node_pos(node - 1)
            angle = sum(self.__motorDegrees[:node])
            angle = sympy.rad(angle)
            x = prev_point[0] + self.__barLength[node - 1] * sympy.cos(angle).evalf()
            y = prev_point[1] + self.__barLength[node - 1] * sympy.sin(angle).evalf()
            return x,y
        else:
            raise ValueError("Invalid node index. Must be 0, 1, or 2.")

    def move_to_with_segments(self, x:float, y:float):
        self.__updateFunction.append(
            SegmentMovementMission(
                self,
                (x,y)
            )
        )

    def rotate(self, degree=0, motor=0):
        # rotate which motor clock wise in how many degrees
        # if not self.__updateFunction:
        #     print("VA: rotation command registration failed")
        #     return
        #this method does not care limitations

        target_degree = self.__motorDegrees[motor] + degree
        is_clockwise = degree > 0
        clockwise_factor = 1 if is_clockwise else -1

        mission = RegRotateMission(
            spd = self.__motorSpeed[motor],
            init_deg= self.__motorDegrees[motor],
            is_clockwise=clockwise_factor,
            target_degree=target_degree,
            motor_number=motor
        )

        self.preempt_mission(mission)

        # self.__updateFunction.append(mission)

        # check no passing point
        pass

    def move_relatively_to(self, x = 0.0, y = 0.0):
        pass

    @staticmethod
    def get_move_to_optimized_plan(machine, x:float,y:float):
        #I am going to return RotatePlan it just not allowing me to type hit that
        #Also I am not able to hint VirtualArms?
        #@Earl

        m:VirtualArms = machine

        from RotatePlan import RotatePlan
        from sympy import Point, Circle, deg, atan2, sqrt, solve, symbols

        # Step 1: Test if the target position is reachable
        target = Point(x, y)
        total_length = sum(m.__barLength)  # Total length of the arm
        distance = Point(0, 0).distance(target)  # Distance from the base to target

        if distance > total_length:
            print("Target point is too far and unreachable!")
            return

        if distance < abs(m.__barLength[0] - m.__barLength[1]):
            print("Target point is too close and unreachable!")
            return

        # Step 2: Set up intersection of circles for possible states
        base = Point(0, 0)  # Base point of the robotic arm
        l1, l2 = m.__barLength  # Length of the two bars (links)

        # Circle centered at the base with radius l1
        circle1 = Circle(base, l1)

        # Circle centered at the target with radius l2
        circle2 = Circle(target, l2)

        # Solve for the intersection points of the two circles
        intersection_points = circle1.intersection(circle2)

        if not intersection_points:
            print("No valid solutions found for the target point!")
            return

        plan_a = RotatePlan(m, intersection_points[0], Point(x, y))
        plan_b = RotatePlan(m, intersection_points[1], Point(x, y))

        best_plan = (None, float("inf"))
        for plan in plan_a.get_valid_plan():
            cost = RotatePlan.solve_plan_cost(plan)
            if cost < best_plan[1]:
                best_plan = (plan, cost)
        for plan in plan_b.get_valid_plan():
            cost = RotatePlan.solve_plan_cost(plan)
            if cost < best_plan[1]:
                best_plan = (plan, cost)

        if best_plan[0] is None:
            print("No valid plan found!")
            return

        return best_plan

        pass

    def move_to_good(self, x=0.0, y=0.0)->bool:

        from RotatePlan import RotatePlan

        optimized_plan:(RotatePlan, float) = VirtualArms.get_move_to_optimized_plan(self,x,y)
        if optimized_plan is None or optimized_plan[0] is None:
            print("No valid plan found!")
            return False
        self.rotate(optimized_plan[0][0], 0)
        self.rotate(optimized_plan[0][1], 1)
        return True

        """
        I guess move_to_good also rest in piece?
        """

        """
        Move the robotic arm to the target (x, y) position.
        This version includes circle intersection calculations to solve for valid positions.

        1. Test if the target position is within reachable range.
        2. Solve possible states by calculating intersection of circles.
        3. Pick one solution and calculate the necessary angles for each motor.

        The process of generating this method is record in a txt file
        """
        from sympy import Point, Circle, deg, atan2, sqrt, solve, symbols

        # Step 1: Test if the target position is reachable
        target = Point(x, y)
        total_length = sum(self.__barLength)  # Total length of the arm
        distance = Point(0, 0).distance(target)  # Distance from the base to target

        if distance > total_length:
            print("Target point is too far and unreachable!")
            return

        if distance < abs(self.__barLength[0] - self.__barLength[1]):
            print("Target point is too close and unreachable!")
            return

        # Step 2: Set up intersection of circles for possible states
        base = Point(0, 0)  # Base point of the robotic arm
        l1, l2 = self.__barLength  # Length of the two bars (links)

        # Circle centered at the base with radius l1
        circle1 = Circle(base, l1)

        # Circle centered at the target with radius l2
        circle2 = Circle(target, l2)

        # Solve for the intersection points of the two circles
        intersection_points = circle1.intersection(circle2)

        if not intersection_points:
            print("No valid solutions found for the target point!")
            return

        plan_a = RotatePlan(self, intersection_points[0], Point(x,y))
        plan_b = RotatePlan(self, intersection_points[1], Point(x,y))


        """
        if a:
        
        if True:
        
        if a == b:
        
        if a is b:
        
        while a:
            break
            
        for a in list:
            
        
        """

        best_plan = (None, float("inf"))
        for plan in plan_a.get_valid_plan():
            cost = RotatePlan.solve_plan_cost(plan)
            if cost < best_plan[1]:
                best_plan = (plan, cost)
        for plan in plan_b.get_valid_plan():
            cost = RotatePlan.solve_plan_cost(plan)
            if cost < best_plan[1]:
                best_plan = (plan, cost)

        if best_plan[0] is None:
            print("No valid plan found!")
            return

        print(type(best_plan[0]))
        print(best_plan[0])
        self.rotate(best_plan[0][0], 0)
        self.rotate(best_plan[0][1], 1)


        # midpoint = intersection_points[0]  # Here, we pick the first solution arbitrarily
        # plan = RotatePlan(self, midpoint, Point(x,y))
        #
        # self.rotate(plan.d0, 0)
        # self.rotate(plan.d1, 1)



    """
            move_to
              RIP
    28-01-2025 - 30-01-2025
    """
    #
    # def move_to(self, x=0.0, y=0.0):
    #     """
    #     Move the robotic arm to the target (x, y) position.
    #     This version includes circle intersection calculations to solve for valid positions.
    #
    #     1. Test if the target position is within reachable range.
    #     2. Solve possible states by calculating intersection of circles.
    #     3. Pick one solution and calculate the necessary angles for each motor.
    #
    #     The process of generating this method is record in a txt file
    #     """
    #     from sympy import Point, Circle, deg, atan2, sqrt, solve, symbols
    #
    #     from RotatePlan import RotatePlan
    #     # Step 1: Test if the target position is reachable
    #     target = Point(x, y)
    #     total_length = sum(self.__barLength)  # Total length of the arm
    #     distance = Point(0, 0).distance(target)  # Distance from the base to target
    #
    #     if distance > total_length:
    #         print("Target point is too far and unreachable!")
    #         return
    #
    #     if distance < abs(self.__barLength[0] - self.__barLength[1]):
    #         print("Target point is too close and unreachable!")
    #         return
    #
    #     # Step 2: Set up intersection of circles for possible states
    #     base = Point(0, 0)  # Base point of the robotic arm
    #     l1, l2 = self.__barLength  # Length of the two bars (links)
    #
    #     # Circle centered at the base with radius l1
    #     circle1 = Circle(base, l1)
    #
    #     # Circle centered at the target with radius l2
    #     circle2 = Circle(target, l2)
    #
    #     # Solve for the intersection points of the two circles
    #     intersection_points = circle1.intersection(circle2)
    #
    #     if not intersection_points:
    #         print("No valid solutions found for the target point!")
    #         return
    #
    #     # Select one valid midpoint (Pick one solution)
    #     # You can choose a specific policy here (e.g., "elbow up" or "elbow down")
    #     midpoint = intersection_points[0]  # Here, we pick the first solution arbitrarily
    #     # print(f"Selected midpoint (joint 2 position): {midpoint}")
    #
    #     # Step 3: Calculate angles based on the selected midpoint
    #     zero_point = Point(0, 0)  # Base (zero) point of the robotic arm
    #
    #     # Angle alpha_1: zero_point -> midpoint
    #     dx1 = midpoint.x - zero_point.x
    #     dy1 = midpoint.y - zero_point.y
    #     alpha_radians_1 = atan2(dy1, dx1)
    #     alpha_1 = deg(alpha_radians_1)  # Convert to degrees
    #     # print(f"Alpha_1 (angle between zero -> midpoint and x-axis): {alpha_1} degrees")
    #
    #     # Angle beta_final_1: midpoint -> target (endpoint)
    #     dx2 = target.x - midpoint.x
    #     dy2 = target.y - midpoint.y
    #     beta_radians_final_1 = atan2(dy2, dx2)
    #     beta_final_1 = deg(beta_radians_final_1)  # Convert to degrees
    #     # print(f"Beta_final_1 (angle between midpoint -> target and x-axis): {beta_final_1} degrees")
    #
    #     # Target angle beta_1 (for second motor)
    #     beta_1 = beta_final_1 - alpha_1
    #     # print(f"Beta_1 (Target degree for motor2): {beta_1} degrees")
    #
    #     # Calculate rotation needed for second motor
    #     motor2_current_degree = self.__motorDegrees[1]  # A method to get motor2's current angle
    #     delta_beta = beta_1 - motor2_current_degree
    #     # print(f"Delta_beta (Rotation needed for motor2): {delta_beta} degrees")
    #
    #     #directly set(temp)
    #     # self.__motorDegrees[0] = alpha_1
    #     # self.__motorDegrees[1] = beta_1
    #
    #     #register moving command
    #     # print(type(delta_beta))
    #
    #     d0 = (alpha_1 - self.__motorDegrees[0]).evalf()
    #     d1 = delta_beta.evalf()
    #     self.rotate(d0, 0)
    #     self.rotate(d1, 1)
    #     print(f"old school: d0 = {d0}, d1 = {d1}")
    #     RotatePlan(self, midpoint, Point(x,y))
    #     # self.rotate((alpha_1 - self.__motorDegrees[0]).evalf(), 0)
    #     # self.rotate(delta_beta.evalf(), 1)
    #
    #
    #
    #     # Step 4: Return computation result for debugging purposes
    #     return {
    #         "intersection_points": intersection_points,
    #         "selected_midpoint": midpoint,
    #         "alpha_1": alpha_1,
    #         "beta_final_1": beta_final_1,
    #         "beta_1": beta_1,
    #         "delta_beta": delta_beta,
    #     }

    def solve_approaching_moves(self, target: Point) -> List[Tuple[str, int]]:
        # show how to rotate motors to move the tip from current point to the target.
        pass

    def planck_degree_rotate(self, degree=True, motor=0):
        # randomly move around 0-2 degree to specified direction.
        # Degree is the direction
        # True for positive, which is counter clock wise
        # Normal distribution
        pass

    def approach(self, target: Point):
        # Move the tip to the target point using plank degree rotate
        pass

    def update(self):

        now = datetime.now()
        delta = now - self.__lastUpdateTime
        self.__lastUpdateTime = now
        # print(f"mission length{len(self.__updateFunction)}")

        if not self.__updateFunction:
            return

        # print(f"current mission len:{len(self.__updateFunction)}")
        # print(self.__updateFunction[0].print_mission())
        # print(self.__updateFunction[1].print_mission())
        mission = self.__updateFunction[0]
        # mission.print_mission()
        mission_accomplished = mission.execute(delta.total_seconds())
        mission_suggested_degree = mission.get_motor_degree()
        mission_suggested_motor = mission.get_focused_motor()
        if mission_suggested_degree is not None and mission_suggested_motor is not None:
            self.__motorDegrees[mission_suggested_motor] \
                = mission_suggested_degree
        # print(self.__motorDegrees[0])
        # print(self.solve_node_pos(2), self.solve_node_pos(1))

        if mission_accomplished:
            # print("popping mission:")
            # mission.print_mission()
            self.__updateFunction.pop(0)
            print("starting mission:")
            # self.__updateFunction[0].print_mission()


if __name__ == "__main__":

    arm = VirtualArms()
    arm.rotate(380)

    while True:
        time.sleep(1)
        arm.update()
