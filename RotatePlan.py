from typing import List, Tuple

from sympy import EmptySet

import VirtualArms
import sympy



class RotatePlan:
    def __init__(self, arm:VirtualArms, midpoint:sympy.Point2D, endpoint:sympy.Point2D):

        self.arm = arm
        self.midpoint = midpoint
        self.endpoint = endpoint
        self.deltaPairs:List[(float, float)] = []

        #Δ = tarfin - prefin - cur
        #tarfin = atan2(dy, dx)
        #prefin 0 = 0

        pre_fin = 0
        pre_pos = sympy.Point2D(arm.solve_node_pos(0))
        dx = midpoint.x - pre_pos.x
        dy = midpoint.y - pre_pos.y
        tarfin = sympy.deg(sympy.atan2(dy, dx))
        cur = arm.get_motor_angle(0)

        self.d0 = (tarfin - pre_fin - cur).evalf()

        pre_fin = tarfin
        pre_pos = midpoint
        dx = endpoint.x - pre_pos.x
        dy = endpoint.y - pre_pos.y
        tarfin = sympy.deg(sympy.atan2(dy, dx))
        cur = arm.get_motor_angle(1)

        self.d1 = (tarfin - pre_fin - cur).evalf()

        self.deltaPairs.append((self.d0, self.d1))
        self.deltaPairs.append((self.delta_reverse(self.d0), self.d1))
        self.deltaPairs.append((self.d0, self.delta_reverse(self.d1)))
        self.deltaPairs.append((self.delta_reverse(self.d0), self.delta_reverse(self.d1)))

        # self.d0 = self.detour_correction(self.d0)
        # self.d1 = self.detour_correction(self.d1)

        # print(f"delta0 = {self.d0} ,delta1 = {self.d1}")

    def detour_correction(self, delta):
        if delta > 180:
            return 360 - delta

        if delta < -180:
            return 360 + delta

        return delta

    def delta_reverse(self, delta):
        if delta > 0:
            return delta - 360
        else:
            return 360 + delta

    @staticmethod
    def solve_plan_cost(plan:(float, float)) -> float:
        return abs(plan[0]) + abs(plan[1])

    def get_valid_plan(self)->List[Tuple[(float, float)]]:
        m0 = self.arm.get_motor_angle(0)
        m1 = self.arm.get_motor_angle(1)
        m0_limit = self.arm.get_motor_interval(0)
        m1_limit = self.arm.get_motor_interval(1)
        prod = []

        for pair in self.deltaPairs:
            interval_0 = sympy.Interval(
                m0,
                m0 + pair[0]
            )
            if interval_0 is EmptySet:
                interval_0 = sympy.Interval(
                    m0 + pair[0],
                    m0
                )
            interval_1 = sympy.Interval(
                m1,
                m1 + pair[1]
            )
            if interval_1 is EmptySet:
                interval_1 = sympy.Interval(
                    m1 + pair[1],
                    m1
                )
            print(f"compare interval: is {interval_0} in {m0_limit} ?")
            print(f"compare interval: is {interval_1} in {m1_limit} ?")
            if not interval_0.is_subset(m0_limit):
                print("bad plan on motor 0")
                continue
            if not interval_1.is_subset(m1_limit):
                print("bad plan on motor 1")
                continue
            prod.append(pair)
        return prod



