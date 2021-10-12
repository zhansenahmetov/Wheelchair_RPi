#!/usr/bin/python
#
#       This program demonstrates how to convert the raw values from an accelerometer to Gs
#
#       The BerryIMUv1, BerryIMUv2 and BerryIMUv3 are supported
#
#       This script is python 2.7 and 3 compatible
#
#       Feel free to do whatever you like with this code.
#       Distributed as-is; no warranty is given.
#
#       https://ozzmaker.com/accelerometer-to-g/

from time import sleep 
from datetime import datetime
import csv
import os
import time
import IMU
import sys



IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
    print(" No BerryIMU found... exiting ")
    sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


file = open("/home/pi/data_log_imu.csv", "a")
if os.stat("/home/pi/data_log_imu.csv").st_size == 0: 
        file.write("Time                       XACC   YACC    ZACC\n")
        
while True:


    #Read the accelerometer,gyroscope and magnetometer values
    ACCx = IMU.readACCx()
    ACCy = IMU.readACCy()
    ACCz = IMU.readACCz()
    yG = (ACCx * 0.244)/1000
    xG = (ACCy * 0.244)/1000
    zG = (ACCz * 0.244)/1000
    print("##### X = %fG  ##### Y =   %fG  ##### Z =  %fG  #####" % ( yG, xG, zG))
    #slow program down a bit, makes the output more readable
    time.sleep(0.03)
    
    now = datetime.now() 
    file.write(str(now)+","+str(format(round(xG,4),'.4f'))+","+str(format(round(yG,4),'.4f'))+","+str(format(round(zG,4),'.4f'))+"\n") 
    file.flush()
    
time.sleep(5)<br>file.close() 


    #slow program down a bit, makes the output more readable
    


