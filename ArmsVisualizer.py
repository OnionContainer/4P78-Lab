from __future__ import annotations
import time
import tkinter as tk
from typing import List, Tuple
import VirtualArms
from Earl import Earl
from MyTk import MyTk
import sympy

class CoordinateDrawer:
    def __init__(self):
        # Initialize the main Tkinter window
        self.window = MyTk()
        self.window.title("Coordinate Drawer")
        self.__targetArm = None

        #init entry block
        entry = tk.Entry(self.window)
        entry.pack()
        entry.focus_set()
        entry.bind("<Return>", self.on_input)
        self.__entry = entry

        #prepare command functions
        self.__current_command_raw = None
        self.__cmd_func_map = {
            "rot": self.cmd_rotate,
            "to": self.cmd_to,
            "rotr": self.cmd_rotate_real,
            "home": self.cmd_home,
            "quit": self.cmd_quit,
            "seg": self.seg_to,
            "sync": self.cmd_sync,
            "esc": self.cmd_esc
        }

        self.__earl = Earl()
        self.__earl.prep()



    def execute_current_command(self):
        if self.__current_command_raw is None:
            return

        command:List[str] = self.__current_command_raw.split(" ")
        func = self.__cmd_func_map.get(command.pop(0))

        if func is None:
            print(f"no command found: {self.__current_command_raw}")
            self.__current_command_raw = None
            return

        self.__current_command_raw = None
        try:
            func(*command)
        except TypeError as e:
            print("invalid argument.\n", e, "\n---···---")
        except IndexError as e:
            print("Turning non existing motor?\n", "\n---···---")
        except ValueError as e:
            print("Type parsing failed. Watch your args.\n", e, "\n---···---")

    def cmd_esc(self):
        self.__earl.excape()

    def cmd_pre(self, index:str = "0"):
        try:
            i = int(index)
        except ValueError as e:
            print("Command parsing problem")
            print(e)
            return
        self.__earl.preset_turn(i)

    def cmd_sync(self):
        self.__targetArm.sync_real(0,0)

    def cmd_quit(self):
        self.__earl.quit()
        self.window.quit()

    def cmd_home(self):
        self.__earl.home()

        pass

    def cmd_rotate_real(self, power="64", degree="5", motor="0", weak="0"):
        try:
            p = int(power)
            d = int(degree)
            m = int(motor)
            w = True if int(weak) == 1 else False
        except ValueError as e:
            print(e)
            return

        self.__earl.turn(p,d,m,w)


        pass

    def seg_to(self, in_x:str = "10.0", in_y:str = "10.0"):
        try:
            x = float(in_x)
            y = float(in_y)
        except ValueError as e:
            print("Command parsing problem")
            print(e)
            return

        self.__targetArm.move_to_with_segments(x,y)
        pass

    def cmd_to(self, in_x:str = "10.0", in_y:str = "10.0"):

        x = float(in_x)
        y = float(in_y)

        # self.__targetArm.move_to(x,y)
        self.window.clear_canvas("target")
        self.window.sign_point(
            (x, y),
            "target",
            f"target({x:.1f},{y:.1f},)",
            shift=(10, -30)
        )
        self.__targetArm.move_to_good(x,y)




        pass

    def cmd_rotate(self, degree:str = "10", motor:str = "0"):
        self.__targetArm.rotate(int(degree), int(motor))

    def on_input(self, event):
        command = self.__entry.get()
        self.__entry.delete(0, tk.END)
        if self.__current_command_raw is None:
            self.__current_command_raw = command
            print(f"command registered: {command}")
        else:
            print(f"command occupied: {self.__current_command_raw}")

    def assign_target_arm(self, arm_to_use:VirtualArms.VirtualArms):
        self.__targetArm = arm_to_use

        def drawStuff(x,y):
            self.window.clear_canvas("target")
            self.window.sign_point(
                (x, y),
                "target",
                f"target({x:.1f},{y:.1f},)",
                shift=(10, -30)
            )

        self.__targetArm.a_random_callback = drawStuff

    def sign_target_arm(self):
        if self.__targetArm is None:
            return

        p1 = self.__targetArm.solve_node_pos(0)
        p2 = self.__targetArm.solve_node_pos(1)
        p3 = self.__targetArm.solve_node_pos(2)

        a0 = self.__targetArm.solve_angle_final(0)
        a1 = self.__targetArm.solve_angle_final(1)

        range1:sympy.Interval = self.__targetArm.get_motor_interval(0)
        range2:sympy.Interval = self.__targetArm.get_motor_interval(1)

        # print(range1.start)
        self.window.clear_fans()

        self.window.draw_fan_contour(
            x=p1[0],
            y=p1[1],
            radius=self.__targetArm.get_bar_length(0),
            start_angle=range1.start,
            extent=range1.measure,
            outline_color="#a1beff",
            width=1
        )

        self.window.draw_fan_contour(
            x=p2[0],
            y=p2[1],
            radius=self.__targetArm.get_bar_length(1),
            extent=range2.measure,
            start_angle=range2.start + a0,
            outline_color="#a1beff",
            width=1
        )

        self.window.sign_line(p1, p2)
        self.window.sign_line(p2, p3)
        self.window.sign_points([p1,p2,p3])

    def dynamic_update(self):
        """Simulate dynamically adding new points."""
        import random
        # new_point = (random.randint(-200, 200), random.randint(-200, 200))
        # neww_point = (float(new_point[0]), float(new_point[1]))
        # self.sign_points([neww_point])
        # self.sign_line((0.0, 0.0), (neww_point[0], neww_point[1]))

        if self.__targetArm is not None:
            self.__targetArm.update()
            self.window.clear_canvas()
            self.sign_target_arm()
        self.execute_current_command()
        # Schedule the next update
        self.window.after(10, self.dynamic_update)

    def run(self):
        """
        Start the Tkinter event loop.
        """
        self.dynamic_update()
        self.window.mainloop()




if __name__ == "__main__":
    # Example usage
    drawer = CoordinateDrawer()
    arm = VirtualArms.VirtualArms()
    # arm.rotate(5720)
    drawer.assign_target_arm(arm)
    drawer.run()


# arm = VirtualArms.VirtualArms()

# while True:
#     time.sleep(1)
#     drawer.sign_points([(x*10, x*-10)])
#     x+=1

"""
1-27
Goal for today
1.Run visualizer and torminal in multithreads
2.Create data shareing mechanism
3.Create command executing mechanism
    visualizer will check command and see if this module can execute it.
    if yes, execute and mark it executed
    if no, vote not executed, command will marked wasted when all vote not executed

"""
