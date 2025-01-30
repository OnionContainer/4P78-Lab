import time
import sys
from time import sleep

import nxt
import nxt.locator
import nxt.motor
import nxt.sensor
import nxt.sensor.generic
from sympy.strategies.core import switch

from book_keeper import BookKeeper

"""
should be something like RealArm or NxtWrap but anyway.
"""
class Earl:

    def __init__(self):
        self.__brick = None
        self.__motor_shoulder = None
        self.__motor_elbow = None
        self.__touch_shoulder = None
        self.__touch_elbow = None
        self.__init_success = False

        trial = 0
        with open("config", "r+") as file:
            trial = int(file.read())
            trial += 1
            file.seek(0)
            file.truncate()
            file.write(trial.__str__())

        print("trial:", trial)
        self.__trial = trial
        self.__book_keeper = BookKeeper(trial)
        #self.__book_keeper.print_log("just to make sure it is useful")

    @staticmethod
    def bumper(sensor):
        def bumpy():
            while not sensor.get_sample():
                pass
            return True
        return bumpy

    def prep(self):

        try:
            self.__brick = nxt.locator.find()
        except nxt.locator.BrickNotFoundError:
            print("---\n<<< Did you remember to turn the brick on? >>>\n---")
            if sys.flags.interactive:
                return
            else:
                #sys.exit(0)
                return
        except Exception as e:
            print(f"don't care\n{e}")
            return

        self.__motor_shoulder = self.__brick.get_motor(nxt.motor.Port.A)
        self.__motor_elbow = self.__brick.get_motor(nxt.motor.Port.B)
        self.__touch_shoulder = self.__brick.get_sensor(nxt.sensor.Port.S1, nxt.sensor.generic.Touch)
        self.__touch_elbow = self.__brick.get_sensor(nxt.sensor.Port.S2, nxt.sensor.generic.Touch)

        self.__init_success = True
        print("Earl: init success")

    def cleanup(self):
        self.__motor_shoulder.idle()
        self.__motor_elbow.idle()
        self.__brick.close()

    def home(self):
        if not self.__init_success:
            print("Earl not initialized")
            return
        self.__motor_shoulder.turn(-15,360,stop_turn=self.bumper(self.__touch_shoulder))
        self.__motor_elbow.turn(15,360,stop_turn=self.bumper(self.__touch_elbow))
        # self.cleanup()

    def preset_turn(self, index:int):
        if not self.__init_success:
            print("Earl not initialized")
            return
        print(f"running preset {index}")

        if index == 0:
            self.turn(64, 5, 0)

        pass

    def quit(self):
        if not self.__init_success:
            print("Earl not initialized")
            return
        self.home()
        self.cleanup()

    def turn(self, power:int, angle:int, motor:int, weak = False):

        print(f"Earl: turn {angle} with {power} on {motor} motor using {weak} weak mode")

        if not self.__init_success:
            print("Earl not initialized")
            return
        if angle < 0:
            angle = -angle
            power = -power

        #self.__book_keeper.print_log(f"state before turning: motor0 on {self.__motor_shoulder.get_tacho()}, motor1 on {self.__motor_elbow.get_tacho()}")
        #log = f"received command: {"weak" if weak else ""} turn motor {motor} by {angle} degrees with power {power}"
        #self.__book_keeper.print_log(log)

        sleep(1)

        self.__motor_shoulder.weak_turn(80, 10)

        if motor == 0:
            if weak:
                print("weak turn shoulder")
                self.__motor_shoulder.weak_turn(
                    power,
                    angle
                )
            print("turn shoulder")
            self.__motor_shoulder.turn(
                power,
                angle,
                stop_turn=self.bumper(self.__touch_shoulder)
            )
        else:
            if weak:
                print("weak turn elbow")
                self.__motor_elbow.weak_turn(
                    power,
                    angle
                )
            print("turn elbow")
            self.__motor_elbow.turn(
                power,

                angle,
                stop_turn=self.bumper(self.__touch_elbow)
            )
        sleep(1)
        #self.__book_keeper.print_log(
        #    f"state after turning: motor0 on {self.__motor_shoulder.get_tacho()}, motor1 on {self.__motor_elbow.get_tacho()}")

        pass


# def running_test():
#
#     for i in range(3):
#         motor_shoulder.weak_turn(64, 1)
#         sleep(1)
#
#     for i in range(3):
#         motor_shoulder.weak_turn(-64, 1)
#         sleep(1)
#
#     for i in range(3):
#         motor_elbow.weak_turn(-64, 1)
#         sleep(1)
#
#     for i in range(3):
#         motor_elbow.weak_turn(64, 1)
#         sleep(1)
#
#
#
# earl = Earl()
# earl.prep()
#cleanup() #Don't do this until you're done, but still check it out!

"""
missions
0.test if the original code is runnable on school machine

1.data collection and manual manipulation

hook this to window, create some commands that can manipulate
for each manipulation create a log, put it in a file
including:
    1.initial position
    2.order executed
    3.final position
  
finally 
  
2.sync mode

a mode that virtual arm will move but will also show the real arm after movement.
before virtual arm moving it will sync to real arm

3.segmentation




"""
