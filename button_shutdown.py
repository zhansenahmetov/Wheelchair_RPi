from gpiozero import Button
from signal import pause
import os, sys

while True:
    print("55")
    offGPIO = int(sys.argv[1]) if len(sys.argv) >= 2 else 21
    holdTime = int(sys.argv[2]) if len(sys.argv) >= 3 else 6
    print("56")
# the function called to shut down the RPI
    def shutdown():
        #os.system("sudo shutdown -h now")
        print("Turning off...")
        print(btn)

    btn = Button(offGPIO, hold_time=holdTime)
    print(btn)
    btn.when_held = shutdown
    pause()    # handle the button presses in the background