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
from bluetooth import *

#######################################BMS functions#######################################

# #write number function for BMS
# def writeNumber(value):
    # bus.write_byte(address, value)
    # return -1

# #read number function for BMS
# def readNumber():
    # number = bus.read_byte_data(address,1)
    # number = 0
    # return number

def get_ESP():
    #MAC address of ESP32
    addr = "A8:03:2A:6A:43:FA"
    #uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    #service_matches = find_service( uuid = uuid, address = addr )
    service_matches = find_service( address = addr )

    #buf_size = 1024;

    if len(service_matches) == 0:
        print("couldn't find the SampleServer service =(")
        sys.exit(0)

    for s in range(len(service_matches)):
        print("\nservice_matches: [" + str(s) + "]:")
        print(service_matches[s])
        
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    port=1
    print("connecting to \"%s\" on %s, port %s" % (name, host, port))

    # Create the client socket
    sock=BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    print("connected")
    
    #sock.send("\nsend anything\n")
    #initialize BMS message of 12 ADC broken measurements
    MSG = [0 for i in range(12)]
    #declare BMS reconstructed ADC values
    results = [0 for i in range(6)]
    
    #initialize BMS measurements
    Totvbat1 = 0
    Totvbat2 = 0
    Totibat = 0
    TotTbat_1 = 0
    TotTbat_2 = 0
    TotAmbTemp = 0
    i=0
    
    #for _ in range(10):
    while True:
        time.sleep(1)
        try:
            t0=time.time()
            sock.send("s")
            MSG = sock.recv(12)
        except:
            print("Bluetooth/BMS error!")
        else:
            if MSG:
                j = [0,1]
                for k in range(6):
                    results[k] = (MSG[j[1]] << 8)+MSG[j[0]]
                    j[0] = j[0] + 2
                    j[1] = j[1] + 2
                    
                #estimates the measurements based on calibration equations 
                #vbat1 = 0.0822*results[0] - 170.06 - 1 #recalibrate
                vbat1 = 0.0102*results[0]+1.5068
                #vbat2 = 0.0822*results[1] - 170.06 - 1 #recalibrate
                vbat2 = 0.0052*results[1]+0.2293
                #ibat = -0.0681*results[2] + 139.84 + 1.22 #recalibrate
                ibat = -0.0832*results[2]+111.74
                Tbat_1 = -0.063*results[3] + 149.71 
                Tbat_2 = -0.0668*results[4] + 157.47
                AmbTemp = -0.0383*results[5] + 100.5
                print("Voltage = ", vbat1, vbat2)
                acqfreq = 1/(time.time()-t0)
                Totvbat1 = Totvbat1+vbat1
                Totvbat2 = Totvbat2+vbat2
                Totibat = Totibat+ibat
                TotTbat_1 = TotTbat_1+Tbat_1
                TotTbat_2 = TotTbat_2+Tbat_2
                TotAmbTemp = TotAmbTemp+AmbTemp
                i=i+1
                #after 5 seconds write all average values in
                if i==5:
                    Avgvbat1 = Totvbat1/i
                    Avgvbat2 = Totvbat2/i
                    Avgibat = Totibat/i
                    AvgTbat_1 = TotTbat_1/i
                    AvgTbat_2 = TotTbat_2/i
                    AvgAmbTemp = TotAmbTemp/i
                    
                    Totvbat1 = 0
                    Totvbat2 = 0
                    Totibat = 0
                    TotTbat_1 = 0
                    TotTbat_2 = 0
                    TotAmbTemp = 0
                    i=0
                    
                    file1=open("WriteGUIBMS.txt","w")
                    file1.write(str(format(round(Avgvbat1,3),'.3f'))+","+str(format(round(Avgvbat2,3),'.3f'))+","+str(format(round(Avgibat,3),'.3f'))+","+str(format(round(AvgTbat_1,3),'.3f'))+","+str(format(round(AvgTbat_2,3),'.3f'))+","+str(format(round(AvgAmbTemp,3),'.3f')))
                    file1.close()

    

#######################################this function handles IMU, BME680, and BMS data acquisition#######################################
def get_I2C():
    print("we are here 1")
    #initialize IMU G values and IMU settings
    xG = 0
    yG = 0
    zG = 0
    IMU.initIMU()
    print("we are here 2")
    #initialize BME680 temperature, humidity, pressure values and I2C
    t = 0
    h = 0
    p = 0
    i2c = I2C(board.SCL, board.SDA)

    print("we are here 3")
    
    #initialize BMS message of 10 ADC broken measurements
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
    print("we are here 4")
    #select I2C bus1 on the Pi, give address for BMS (75)
    bus = smbus.SMBus(1)
    address = 0x04
    
    #create the I2C data log file
    date1 = date.today()
    time1 = datetime.now().strftime("%H:%M:%S")
    name1 = "data_log_I2C_{}_{}.csv".format(date1,time1)
    print("we are here 5")
    #name of the csv file will be saved in txt
    file1=open("csvName.txt","w")
    file1.write(name1)
    file1.close()
    
    file1 = open(name1, 'w', newline='')
    writer1 = csv.writer(file1)
    writer1.writerow(["CPU Time", "Time", "AccX(G)", "AccY(G)", "AccZ(G)",\
                      "Ambient(degC)", "Humidity(%)", "Pressure(hPa)", "Acquisition Frequency"])
    
    #initialize totalI, totalV, totalzG values for averaging each 5 sec and showing on GUI
    totalzG=0
    totalyG=0
    i=0
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
            time.sleep(0.01)
            
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
            time.sleep(0.01)
            

        #get the system timestamp
        now = datetime.now()
        
        #data acquisition frequency (NOTE: this is just the speed the code gets all the data, not the frequency at which it is being stored)
        acqfreq = 1/(time.time()-t0)
        
        #Get CPU time for indexing data
        t_cpu = time.time()
        
        #store all of our data in the csv file
        writer1.writerow([str(t_cpu), str(now), str(format(round(xG,3),'.3f')), str(format(round(yG,3),'.3f')),\
                 str(format(round(zG,3),'.3f')), str(t), str(h), str(p), str(format(round(acqfreq,3),'.3f'))])
        
        #each 5 seconds get the average value of temp, I, V and zG(for now)
        i=i+1

        totalzG=totalzG+zG
        totalyG=totalyG+yG
        #after 5 seconds write all average values in
        if i==5:

            avgzG=totalzG/i
            avgyG=totalyG/i
            
            totalzG=0
            totalyG=0
            i=0
            file1=open("WriteGUI.txt","w")
            file1.write(str(format(round(avgzG,3),'.3f'))+","+str(format(round(avgyG,3),'.3f')))
            file1.close()

        #we want a stable 5Hz operating frequency, so wait the time difference to achieve this 
        wait = 1-time.time()+t0
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
    #Changed serial port for GPS with 9600 baud rate, 5s timeout; GPS updates at 10Hz
    ser = serial.Serial('/dev/serial0', 9600, timeout=5)
    print("Connected to: ", '/dev/serial0')
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    
    #create the GPS data log file
    date1 = date.today()
    time1 = datetime.now().strftime("%H:%M:%S")
    name2 = "data_log_GPS_{}_{}.csv".format(date1,time1)
    file2 = open(name2, 'w', newline='') 
    writer2 = csv.writer(file2)
    writer2.writerow(["CPU Time", "Time", "GPS time", "Latitude", "Lat. Direction", "Longitude", "Long. Direction", "Num. Satellites", "Speed(km/h)"])
    
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
            #get the system timestamp
            now = datetime.now()
            
            #Get CPU time for indexing data
            t_cpu = time.time()
            
            #we have new data, store everything
            writer2.writerow([str(t_cpu), str(now), str(GPStime)[:-5], str(lat), str(latd), str(lon),\
                             str(lond), str(numsat), speed])
            #reset GPS data values we are checking
            lat = 0
            speed = 0
            
            print("Wrote GPS waypoint!")
            
#######################################execution starts here#######################################
#get_I2C()
#get_serial()
def runProgram():
    with concurrent.futures.ProcessPoolExecutor() as executor:
         f1 = executor.submit(get_I2C)
         f2 = executor.submit(get_serial)
         f3 = executor.submit(get_ESP)
#runProgram()
#get_ESP()