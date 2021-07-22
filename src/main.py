import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, '../lib'))
sys.path.insert(0, lib_dir)

import Leap

class Listener(Leap.Listener):

    def on_connect(self, controller):
        print("Connected")


    def on_frame(self, controller):
        frame = controller.frame()

        print("Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
            frame.id, frame.timestamp, len(frame.hands), len(frame.fingers)))

def main():
    listener = Listener()
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
