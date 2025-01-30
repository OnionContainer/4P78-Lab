import random
from abc import ABC, abstractmethod
import sympy
from sympy import Point2D, false

config = {
    "segSize": 5.0
}

class ArmMission(ABC):
    @abstractmethod
    def execute(self, delta_time:float)->bool:
        pass

    @abstractmethod
    def get_motor_degree(self)->float:
        pass

    @abstractmethod
    def print_mission(self):
        pass

    @abstractmethod
    def get_focused_motor(self)->int:
        pass


class RegRotateMission(ArmMission):
    def __init__(self, spd, init_deg, is_clockwise, target_degree, motor_number):
        self.__motorSpeed = spd
        self.__motorDegree = init_deg
        self.__is_clockwise = is_clockwise
        self.__targetDegree = target_degree
        self.motor_number = motor_number

        """
        5/3 = 5/3
        float = float.max
        :)
        ：）
        """

        # print(f"target({target_degree}), current({deg}), motor({motor_number}), spd({spd}), clockwise({is_clockwise})")
        pass

    def get_focused_motor(self):
        return self.motor_number

    def print_mission(self):
        print(f"target({self.__targetDegree}), current({self.__motorDegree}), motor({self.motor_number}), spd({self.__motorSpeed}), clockwise({self.__is_clockwise})")

    def get_motor_degree(self):
        return self.__motorDegree

    def execute(self, delta_time:float)->bool:
        movement = delta_time * self.__motorSpeed * self.__is_clockwise
        new_angle = self.__motorDegree + movement
        if self.__is_clockwise > 0 and new_angle > self.__targetDegree:
            self.__motorDegree = self.__targetDegree
            return True
        elif not self.__is_clockwise > 0 and new_angle < self.__targetDegree:
            self.__motorDegree = self.__targetDegree
            return True

        self.__motorDegree = new_angle

        return False
        pass


class SegmentMovementMission(ArmMission):
    def __init__(self, arm, target:(float, float)):
        from VirtualArms import VirtualArms
        if type(arm) is not VirtualArms:
            raise Exception("wrong arm type")
        self.__arm: VirtualArms = arm
        self.__target = target
        self.__current_target = None
        self.__bypass_points = []
        # AI code starts[field 1]

        # Convert current position to Point2D object
        current_position = Point2D(self.__arm.solve_node_pos(2))  # Assume self.__arm.get_position() returns (x, y)

        # Convert target position to Point2D object
        target_position = Point2D(self.__target)  # Assume self.__target is the target position (x, y)

        # Define the segment size (interval between points)
        seg_size = config["segSize"]

        # Calculate the distance between current and target positions
        distance = current_position.distance(target_position)

        # Calculate the normalized direction vector
        if distance == 0:  # If no distance, set the normalized vector to zero
            normalized_vector = Point2D(0, 0)
        else:
            normalized_vector = (target_position - current_position) / distance

        # Calculate the number of bypass segments
        num_segments = int(distance // seg_size)

        # Generate the intermediate bypass points
        for i in range(1, num_segments):
            point = current_position + normalized_vector * seg_size * i  # Generate new points along the path
            self.__bypass_points.append((float(point.x), float(point.y)))  # Append points as (x, y) tuples

        # Append the target position to the list
        self.__bypass_points.append((float(target_position.x), float(target_position.y)))  # Ensure target included

        # AI code ends[field 1]





    def get_focused_motor(self):
        pass

    def get_motor_degree(self):
        pass

    def print_mission(self):
        pass

    def execute(self, delta_time: float)->bool:
        if self.__arm.get_current_mission() is not self:
            raise Exception("What is going on with mission?")

        # self.__arm.rotate(random.choice([-1,1])* random.randint(30,90), random.randint(0,1))

        # x = random.uniform(30,100) * random.choice([-1,1])
        # y = random.uniform(30, 100) * random.choice([-1, 1])
        # # x,y = random.uniform(0,100),random.uniform(-100,100)
        # self.__arm.a_random_callback(x,y)
        # self.__arm.move_to_good(
        #     x,y
        # )

        if self.__bypass_points:
            p = self.__bypass_points.pop(0)
            self.__arm.a_random_callback(p[0],p[1])
            is_target_valid = self.__arm.move_to_good(p[0],p[1])
            if not is_target_valid:
                self.__bypass_points = []
                return True
            return False

        return True

        # new_mission = RegRotateMission(
        #     spd=45,
        #     init_deg=self.__arm.get_motor_angle(0),
        #     is_clockwise=random.choice([-1,1]),
        #     target_degree=random.randint(0,360),
        #     motor_number=0
        # )
        #
        # new_mission.print_mission()
        #
        # self.__arm.preempt_mission(
        #     new_mission
        # )

        """
        if current mission is self
        check if all movement is performed
    
        if not:
            create and preempt RegRotateMission
            
        if yes:
            return True
        
        """

        pass

