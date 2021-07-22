import os
import sys
import inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, '../lib'))
sys.path.insert(0, lib_dir)

import Leap

from arduino_serial import Angles, connect, set_angles, set_speed
from ik import Position, braccio_ik

ARDUINO_SERIAL_PATH = '/dev/ttyACM0'


class BraccioListener(Leap.Listener):

    def __init__(self, serial):
        super(BraccioListener, self).__init__()
        self.serial = serial
        set_speed(self.serial, 10)

    def on_connect(self, controller):
        print("Connected")

    def on_frame(self, controller):
        frame = controller.frame()

        if len(frame.hands) < 1:
            print("No hands")
            return

        if len(frame.hands) > 1:
            print("More than one hand")
            return

        hand = frame.hands[0]
        print("Frame id: %d, timestamp: %d, palm_position: %s" % (
            frame.id, frame.timestamp, hand.palm_position))

        # Z axis (height) for the braccio corresponds to y axis for leapmotion
        # and y axis is flipped
        x = hand.palm_position.x
        y = hand.palm_position.z
        z = hand.palm_position.y

        self._move_braccio(x, y, z)

    def _move_braccio(self, x, y, z):
        # fixed angles
        wrist_rot = 90
        gripper = 40

        target_pos = Position(x, y, z)
        ik_angles = braccio_ik(target_pos)

        if ik_angles is None:
            print("position unreachable")
            return

        angles = Angles(
            base=ik_angles.base,
            shoulder=ik_angles.shoulder,
            elbow=ik_angles.elbow,
            wrist_ver=ik_angles.wrist_ver,
            wrist_rot=wrist_rot,
            gripper=gripper,
        )

        set_angles(self.serial, angles)


def main():
    print("connecting to the Braccio...")
    serial = connect(ARDUINO_SERIAL_PATH)
    print("connected")

    listener = BraccioListener(serial)
    controller = Leap.Controller()
    controller.add_listener(listener)

    print("Press Enter to quit...")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
