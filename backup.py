from datetime import datetime
from datetime import date
from busio import I2C
from time import sleep
from gpiozero import Button
from signal import pause
import os, sys
import time
import os
import csv
import sys
import board
import adafruit_bme680
import IMU
import smbus
import io
import pynmea2
import serial

#initialize GPS serial port
ser = serial.Serial('/dev/serial0', 9600, timeout=5.0)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

#initialize IMU G values and IMU settings
xG=0
yG=0
zG=0
IMU.initIMU()

#initialize BME680 temperature, humidity, pressure values and I2C
t=0
h=0
p=0
i2c = I2C(board.SCL, board.SDA)

#initialize BMS measurements
vbat=0
ibat=0
Tbat_1 = 0
#declare BMS message of 10 ADC broken measurements
MSG = [0 for i in range(10)]
#declare BMS reconstructed ADC values
results = [0 for i in range(5)]

#try to connect to BME680
try:
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
    bme680.sea_level_pressure = 1013.25
    temperature_offset = -1.8
except:
    print("BME680 not connected")

#select I2C bus1 on the Pi, give address for BMS (75)
bus = smbus.SMBus(1)
address = 0x75

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte_data(address,1)
    number = 0
    return number

#create a new data log file, name is: data_log_{date}_{time}
date = date.today()
time1 = datetime.now().strftime("%H:%M:%S")
name = "data_log_{}_{}".format(date,time1)
with open(name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Voltage", "Current", "Temp1", "Temp2", "Temp3", "AccX(G)", "AccY(G)", "AccZ(G)", "Ambient(degC)", "Humidity(%)", "Pressure(hPa)"])

    btn = Button(21)

    while True:
        t0=time.time()
        
        #try to get IMU readings
        try:
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            print("IMU Works")
        except:
            print("IMU Error!")
        else:
            yG = (ACCx * 0.244)/1000
            xG = (ACCy * 0.244)/1000
            zG = (ACCz * 0.244)/1000
            
        #debug print statements, leave commented
        #print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
        #print("Gas: %d ohm" % bme680.gas)
        #print("Humidity: %0.1f %%" % bme680.relative_humidity)
        #print("Pressure: %0.3f hPa" % bme680.pressure)
        #print("Altitude = %0.2f meters" % bme680.altitude)
        #print("##### X = %fG  ##### Y =   %fG  ##### Z =  %fG  #####" % ( yG, xG, zG))

        #try to get BME680 readings
        try:
            temp=bme680.temperature
            hum=bme680.relative_humidity
            pres=bme680.pressure
            print("BME works")
        except:
            print("BME680 Error!")
        else:
            t=format(round(temp+temperature_offset,3),'.3f')
            h=format(round(hum,3),'.3f')
            p=format(round(pres,3),'.3f')
            
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
            
        
        

        now = datetime.now()
#         file.write(str(now)+","+str(format(round(vbat,3),'.3f'))+","+str(format(round(ibat,3),'.3f'))+","+str(format(round(vbat,3),'.3f'))+ \
#                    ","+str(format(round(vbat,3),'.3f'))+","+str(format(round(vbat,3),'.3f'))+","+str(format(round(xG,3),'.3f'))+ \
#                    ","+str(format(round(yG,3),'.3f'))+","+str(format(round(zG,3),'.3f'))+","+str(t)+ \
#                    ","+str(h)+","+str(p)+"\n")
        writer.writerow([str(now), str(format(round(vbat,3),'.3f')), str(format(round(vbat,3),'.3f')), str(format(round(27.55,3),'.3f')),\
                         str(format(round(vbat,3),'.3f')), str(format(round(vbat,3),'.3f')), str(format(round(xG,3),'.3f')), str(format(round(yG,3),'.3f')),\
                         str(format(round(zG,3),'.3f')), str(t), str(h), str(p)])
        #file.flush()
        #print("Iteration time:",time.time()-t0)
        print("Frequency:",1/(time.time()-t0))
        
        #if btn.is_pressed:
            #os.system("sudo shutdown -h now")
            
