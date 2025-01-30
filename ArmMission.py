import random
from abc import ABC, abstractmethod
import sympy

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


    def get_focused_motor(self):
        pass

    def get_motor_degree(self):
        pass

    def print_mission(self):
        pass

    def execute(self, delta_time: float):
        if self.__arm.get_current_mission() is not self:
            raise Exception("What is going on with mission?")

        # self.__arm.rotate(random.choice([-1,1])* random.randint(30,90), random.randint(0,1))

        x = random.uniform(30,100) * random.choice([-1,1])
        y = random.uniform(30, 100) * random.choice([-1, 1])
        # x,y = random.uniform(0,100),random.uniform(-100,100)
        self.__arm.a_random_callback(x,y)
        self.__arm.move_to_good(
            x,y
        )

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

