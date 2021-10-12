import os
from time import sleep
import RPi.GPIO as GPIO

###################################
#              SETUP              #
###################################

#disabeling in use warning
GPIO.setwarnings(False)

#switching to BCM mode
GPIO.setmode(GPIO.BCM)

#setting up GPIO 22 as on input
GPIO.setup(22, GPIO.IN)

#setting up GPIO 27 as output pulled low
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW)

while True:    
    if GPIO.input(22):
        os.system("sudo shutdown -h now")
#         print("shutdown")
#         sleep(0.5)