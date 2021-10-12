from datetime import datetime
from datetime import date
from busio import I2C
from gpiozero import Button
from signal import pause
from io import BytesIO
import os, sys
import time
import csv
import sys
import board
import adafruit_bme680
import IMU
import smbus
import io
import pynmea2
import serial
import concurrent.futures

#######################################BMS functions#######################################

#write number function for BMS
def writeNumber(value):
    bus.write_byte(address, value)
    return -1

#read number function for BMS
def readNumber():
    number = bus.read_byte_data(address,1)
    number = 0
    return number

#######################################this function handles IMU, BME680, and BMS data acquisition#######################################
def get_I2C():
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
    vbat = 0
    ibat = 0
    Tbat_1 = 0
    Tbat_2 = 0
    AmbTemp = 0
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
    
    #create the I2C data log file
    date1 = date.today()
    time1 = datetime.now().strftime("%H:%M:%S")
    name1 = "data_log_I2C_{}_{}.csv".format(date1,time1)
    file1 = open(name1, 'w', newline='')
    writer1 = csv.writer(file1)
    writer1.writerow(["Time", "Voltage", "Current", "Temp1", "Temp2", "Temp3(AmbientBMS)", "AccX(G)", "AccY(G)", "AccZ(G)",\
                      "Ambient(degC)", "Humidity(%)", "Pressure(hPa)", "Acquisition Frequency"])
    
    #infinite loop to sample and store data from I2C devices
    while True:
        t0=time.time()
        #try to get IMU readings
        try:
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
        except:
            print("IMU Error!")
        else:
            yG = (ACCx * 0.244)/1000
            xG = (ACCy * 0.244)/1000
            zG = (ACCz * 0.244)/1000
            
        #try to get BME680 readings
        try:
            temp=bme680.temperature
            hum=bme680.relative_humidity
            pres=bme680.pressure
        except:
            print("BME680 Error!")
        else:
            t=format(round(temp+temperature_offset,3),'.3f')
            h=format(round(hum,3),'.3f')
            p=format(round(pres,3),'.3f')
            
        #try to get BMS readings
        try:
            #sends command to BMS to initiate data transmission
            bus.write_byte(address, 12)
            for i in range(10):
                MSG[i] = bus.read_byte_data(address,1)
        except:
            print("BMS Error!")
        else:
            #reconstructs the 16-bit ADC measurement  
            j = [0,1]
            for k in range(5):
                results[k] = (MSG[j[1]] << 8)+MSG[j[0]]
                j[0] = j[0] + 2
                j[1] = j[1] + 2
            #estimates the measurements based on calibration equations 
            vbat = 0.0822*results[0]- 170.06
            ibat = -0.0681*results[1] + 139.84
            Tbat_1 = -0.063*results[2] + 149.71
            Tbat_2 = -0.0668*results[3] + 157.47
            AmbTemp = -0.0383*results[4] + 100.5
            #print("V_battery = %.2f, I_battery = %.2f,  Temp1 = %.2f" % (vbat, ibat, Tbat_1))
            
        #get the system timestamp
        now = datetime.now()
        
        #data acquisition frequency (NOTE: this is just the speed the code gets all the data, not the frequency at which it is being stored)
        acqfreq = 1/(time.time()-t0)
        
        #store all of our data in the csv file
        writer1.writerow([str(now), str(format(round(vbat,3),'.3f')), str(format(round(ibat,3),'.3f')), str(format(round(Tbat_1,3),'.3f')),\
                 str(format(round(Tbat_2,3),'.3f')), str(format(round(AmbTemp,3),'.3f')), str(format(round(xG,3),'.3f')), str(format(round(yG,3),'.3f')),\
                 str(format(round(zG,3),'.3f')), str(t), str(h), str(p), str(format(round(acqfreq,3),'.3f'))])
        
        #we want a stable 100Hz operating frequency, so wait the time difference to achieve this 
        wait = 0.0099-time.time()+t0
        if wait<0:
            print("FrequencyI2C:",1/(time.time()-t0))
            continue
        else:
            time.sleep(wait)
            print("FrequencyI2C:",1/(time.time()-t0))

#######################################this function handles GPS data acquisition#######################################
def get_serial():
    #initialize GPS readings
    lat = 0
    latd = 0
    lon = 0
    lond = 0
    numsat = 0
    GPStime = 0
    speed = 0
    t0 = 0

    #initialize serial port for GPS with 115200 baud rate, 5s timeout; GPS updates at 10Hz
    ser = serial.Serial('/dev/serial0', 115200, timeout=5)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    
    #create the GPS data log file
    date1 = date.today()
    time1 = datetime.now().strftime("%H:%M:%S")
    name2 = "data_log_GPS_{}_{}.csv".format(date1,time1)
    file2 = open(name2, 'w', newline='') 
    writer2 = csv.writer(file2)
    writer2.writerow(["GPS time", "Latitude", "Lat. Direction", "Longitude", "Long. Direction", "Num. Satellites", "Speed(km/h)"])
    
    #infinite loop to sample and store GPS data
    while True:
        #try to get GPS readings
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)
            NMEAsen = str(msg)
            #look for GNGGA and GNVTG sentences; these have the info we want (use pynmea2 and string parsing), otherwise continue
            if NMEAsen[0:6]=="$GNGGA":
                lat = msg.latitude
                latd = msg.lat_dir
                lon = msg.longitude
                lond = msg.lon_dir
                numsat = msg.num_sats
                GPStime = msg.timestamp
                if len(str(GPStime))==8:
                    GPStime = str(GPStime)+'.000000'
            elif NMEAsen[0:6]=="$GNVTG":
                splitsen = NMEAsen.split(",")
                speed = splitsen[7]
            else:
                continue
        except:
            print("GPS error!")
            
        #we only want to store data when we have new values, continue if we are waiting on one
        if lat==0 or speed==0:
            continue
        else:
            #we have new data, store everything
            writer2.writerow([str(GPStime)[:-5], str(format(round(lat,3),'.3f')), str(latd), str(format(round(lon,3),'.3f')),\
                             str(lond), str(numsat), speed])
            #reset GPS data values we are checking
            lat = 0
            speed = 0
            
#######################################execution starts here#######################################
#get_I2C()
#get_serial()
with concurrent.futures.ProcessPoolExecutor() as executor:
    f1 = executor.submit(get_I2C)
    f2 = executor.submit(get_serial)
