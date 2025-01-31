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

    def start_recording(self):
        self.__turning_start_time = time.time()
        self.__turning_start_angle = self.__motor_shoulder.get_tacho().rotation_count
        pass

    def get_motor_degree(self, motor:int)->float:
        if motor == 0:
            return self.__motor_shoulder.get_tacho().rotation_count
        else:
            return self.__motor_elbow.get_tacho().rotation_count

    def __init__(self):
        self.__brick = None
        self.__motor_shoulder = None
        self.__motor_elbow = None
        self.__touch_shoulder = None
        self.__touch_elbow = None
        self.__init_success = False

        self.__turning_start_time = None
        self.__turning_start_angle = None

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
    def bumper(sensor, init_time, init_deg, get_deg, tar_dis):

        t = init_time
        d = init_deg
        g = get_deg
        tar = tar_dis

        print("bumpy test start")

        def bumpy():
            while not sensor.get_sample():
                print("-", end="")
                if time.time() - t > 2:
                    print("bumpy return True due to timeout")
                    return True
                if abs(g() - d) > tar:
                    print("bumpy return True due to angle reached")
                    return True
            return True
        return bumpy

    @staticmethod
    def fummer(sensor):


        def fummy():
            while not sensor.get_sample():
                pass
            return True
        return fummy

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
        self.__motor_shoulder.turn(-15,360,stop_turn=Earl.fummer(
            self.__touch_shoulder
        ))
        self.__motor_elbow.turn(15,360,stop_turn=Earl.fummer(self.__touch_elbow))
        self.__motor_shoulder.reset_position(False)
        self.__motor_elbow.reset_position(False)
        self.print_status()
        sleep(1)
        self.__motor_shoulder.idle()
        self.__motor_elbow.idle()
        # self.cleanup()

    def preset_turn(self, index:int):
        if not self.__init_success:
            print("Earl not initialized")
            return
        print(f"running preset {index}")

        if index == 0:
            self.turn(64, 5, 0)

        pass

    def excape(self):
        print("escape from zero")
        self.print_status()
        sleep(1)
        self.__motor_shoulder.weak_turn(100,5)
        sleep(1)
        self.__motor_elbow.weak_turn(-100,5)
        sleep(1)
        self.print_status()

    def quit(self):
        if not self.__init_success:
            print("Earl not initialized")
            return
        self.home()
        self.cleanup()

    def print_status(self):
        print(f"shoulder: {self.__motor_shoulder.get_tacho().rotation_count} elbow: {self.__motor_elbow.get_tacho().rotation_count}")
        
    def segment_turn(self, power:int, angle:int, motor:int, weak = False):
        target_deg = self.get_motor_degree(motor) + angle
        angle = 1 if angle > 0 else -1
        while True:
            self.turn(power, angle, motor, weak)
            #this should be some validated good parameter
            #angle is +-1 unchanged. adjust weak and power

            # sleep(1)
            deg = self.get_motor_degree(motor)
            if angle > 0 and deg >= target_deg:
                print("segment turns end")
                break
            elif angle < 0 and deg <= target_deg:
                print("segment turns end")
                break
            else:
                print("segment turn occur")
                continue



    def turn(self, power:int, angle:int, motor:int, weak = False):

        print(f"Earl: turn {angle} with {power} on {motor} motor using {weak} weak mode")
        self.__motor_shoulder.idle()
        self.__motor_elbow.idle()

        if not self.__init_success:
            print("Earl not initialized")
            return
        if angle < 0:
            angle = -angle
            power = -power

        tar_dis = abs(angle)
        gett = None

        def g1():
            return self.__motor_shoulder.get_tacho().rotation_count
        def g2():
            return self.__motor_elbow.get_tacho().rotation_count

        if motor == 0:
            gett = g1
        else:
            gett = g2

        #self.__book_keeper.print_log(f"state before turning: motor0 on {self.__motor_shoulder.get_tacho()}, motor1 on {self.__motor_elbow.get_tacho()}")
        #log = f"received command: {"weak" if weak else ""} turn motor {motor} by {angle} degrees with power {power}"
        #self.__book_keeper.print_log(log)

        self.print_status()
        sleep(0.1)

        #self.__motor_shoulder.weak_turn(80, 10)

        if motor == 0:
            if weak:
                print("weak turn shoulder")
                self.__motor_shoulder.weak_turn(
                    power,
                    angle
                )
            else:
                print("turn shoulder")
                self.__motor_shoulder.turn(
                    power,
                    angle,
                    stop_turn=Earl.bumper(
                        self.__touch_shoulder,
                        time.time(),
                        self.__motor_shoulder.get_tacho().rotation_count,
                        gett,
                        tar_dis
                    )
                )
        else:
            if weak:
                print("weak turn elbow")
                self.__motor_elbow.weak_turn(
                    power,
                    angle
                )

            else: 
                print("turn elbow")
                
                self.__motor_elbow.turn(
                    power,
                    angle,
                    stop_turn=Earl.bumper(
                        self.__touch_elbow,
                        time.time(),
                        self.__motor_elbow.get_tacho().rotation_count,
                        gett,
                        tar_dis
                    )
                )
        # print("paused here?")
        sleep(0.1)
        self.print_status()
        # print("paused herere?")
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
