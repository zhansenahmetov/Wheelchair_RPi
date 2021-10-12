from datetime import datetime
from datetime import date
from busio import I2C
from time import sleep
from gpiozero import Button
from signal import pause
import os, sys
import time
import sys
import board
import smbus

#initialize BMS measurements
vbat=0
ibat=0
Tbat_1 = 0

#declare BMS message of 10 ADC broken measurements
MSG = [0 for i in range(10)]

#declare BMS reconstructed ADC values
results = [0 for i in range(5)]


#select I2C bus1 on the Pi, give address for BMS (75)
bus = smbus.SMBus(1)
address = 0x75

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte_data(address,1)
    return number
print("Got here")
while True:
#BMS section
#     BMS_control = input("Receive from BMS >>> HOLD Enter!")
#     if(BMS_control == ""):
    try:
        #Sends command to BMS to initiat data transmission
        writeNumber(12)
        for i in range(10):
            MSG[i] = readNumber()
            
    except:
        print("BMS Error!")
        
    else:
                #Reconstructs the 16-bit ADC measurement  
        j = [0,1]
        for k in range(5):
            results[k] = (MSG[j[1]] << 8)+MSG[j[0]]
            j[0] = j[0] + 2
            j[1] = j[1] + 2
         
        #Estimates the measurements based on calibration equations 
        vbat = 0.0822*results[0]- 170.06
        ibat = -0.0681*results[1] + 139.84
        Tbat_1 = -0.063*results[2] + 149.71
        print("V_battery = %.2f, I_battery = %.2f,  Temp1 = %.2f" % (vbat, ibat, Tbat_1))
        


