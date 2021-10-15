"""
This file controls sensor measurements for the Wheelchair
"""

from datetime import datetime
from datetime import date
from busio import I2C
from gpiozero import Button
#from signal import pause
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
from dateutil.relativedelta import relativedelta
import pickle5 as pickle
import subprocess

#######################################BMS functions#######################################

update_once=0; #not updated now
gdt = 0.2 # each gdt seconds the data is taken from esp
csv_time = 5 #each csv_time*gdt seconds the data is saved into csv
# if csv_time is 5 and gdt 0.1 then csv file will write every 5*0.1=0.5 seconds


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
# This part is for getting the last time the Pi was shutdown properly (If power was cut from the RPi without pressing the shutdown, this method cannot work!)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']   # Month codes as stored in the RPi OS

#  
cmd = 'last -x shutdown | head -1'
try:
    result = subprocess.check_output(cmd, shell=True)
    sd_time = result[43:55].decode()
except Exception as e:
    print("command failed: ",e)


# This function should be called in the main code in the get_I2C() function
def SoC(sd_time, dt, ibat, vbat):
    """
    This function updates the State Of Charge (SoC)
    :param sd_time: last shutdown time
    :param dt: change in time
    :param ibat: current of the battery
    :param vbat: voltage of the battery
    """
    global update_once
    # Load last SoC from the .pkl file 
    # Open the file in binary mode
    with open('SoC.pkl', 'rb') as file:
        myVar = pickle.load(file)
    
    Q_n = 55*3600   #Nominal charge in [C] > note: it is current dependent
    
    # Experimental SoC table (from battery_modeling_script_v2)
    # V_oc_final_fit1 = p1.*x + p2;
    p1 = 0.01312;
    p2 = 11.67;
    
    # Last proper shutdown month, day, hour, and minute
    sd_month_str= sd_time[0:3]
    sd_month = months.index(sd_month_str)+1
    sd_day = int(sd_time[3:7])
    sd_hr = int(sd_time[7:9])
    sd_min = int(sd_time[10:])

    # The month, day, hour, and minute now
    now_min = datetime.now().minute
    now_hr = datetime.now().hour
    now_day = datetime.now().day
    now_mon = datetime.now().month
    
    # Get V_oc is the battery has rested for at least 45 minutes and the battery current is almost zero
    rest_time = (now_hr*60 + now_min) - (sd_hr*60 + sd_min)
    
    if update_once==0:
        if now_mon == sd_month and now_day == sd_day and rest_time > 45  and -0.5<ibat<0.7:
            myVar[0] = vbat             # myVar[0] is the open-circuit voltage
            myVar[1] = (vbat - p2)/p1   # myVar[0] is the SoC (Capacity)
            print("SoC updated 1!")
            update_once=1
        elif now_mon == sd_month and now_day > sd_day and -0.5<ibat<0.7:
            myVar[0] = vbat
            myVar[1] = (vbat - p2)/p1
            print("SoC updated 2!")
            update_once=1
        elif now_mon > sd_month and -0.5 < ibat < 0.7:
            myVar[0] = vbat
            myVar[1] = (vbat - p2)/p1
            print("SoC updated 3!")
            update_once=1
    
    #Estimate and return SoC = myVar[1]
    myVar[1] = myVar[1] - ibat*dt/Q_n
    #print("SoC = ", myVar[1])
    
    # Use dump() to save the updated SoC and open-circuit voltage in the same 
    with open('SoC.pkl', 'wb') as file:
        pickle.dump(myVar, file)
    return myVar[1]



#######################################this function handles IMU, BME680, and BMS data acquisition#######################################
def get_I2C():
    """
    This function communicates with the IMU, BME680, and BMS sensors over I2C to acquire data
    """
    #initalize BMS connection
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
    TotSoc=0
    i=0
    jk=0

    
    #print("we are here 1")
    #initialize IMU G values and IMU settings
    xG = 0
    yG = 0
    zG = 0
    IMU.initIMU()
    #print("we are here 2")
    #initialize BME680 temperature, humidity, pressure values and I2C
    t = 0
    h = 0
    p = 0
    i2c = I2C(board.SCL, board.SDA)

    #print("we are here 3")
    

    #try to connect to BME680
    try:
        bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
        bme680.sea_level_pressure = 1013.25
        temperature_offset = -1.8
    except:
        print("BME680 not connected")
    #print("we are here 4")
    #select I2C bus1 on the Pi, give address for BMS (75)
    bus = smbus.SMBus(1)
    address = 0x04
    
    #create the I2C data log file
    date1 = date.today()
    time1 = datetime.now().strftime("%H:%M:%S")
    name1 = "data_log_I2C_{}_{}.csv".format(date1,time1)
    #print("we are here 5")
    #name of the csv file will be saved in txt
    file1=open("csvName.txt","w")
    file1.write(name1)
    file1.close()
    csv_headers = [
                "CPU Time",
                "Time",
                "AccX(G)",
                "AccY(G)",
                "AccZ(G)",
                "Ambient(degC)",
                "Humidity(%)",
                "Pressure(hPa)",
                "Acquisition Frequency",
                "V_bat_1",
                "V_bat_2",
                "I_bat",
                "T_bat_1",
                "T_bat_2",
                "Ambient_Temp",
                "SoC_value"
            ]
    #initialize csv headers
    with open(name1,'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
    

    tx=time.time()-0.135; # at the beggining set it to 0.2 seconds, 0.135 since 0.065 seconds taken to get all data
    #infinite loop to sample and store data from I2C and ESP devices
    while True:
        t0=time.time()
        #try to get BMS readings
        try:
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
                vbat1 = round(0.0102*results[0]+1.5068,3)
                #vbat2 = 0.0822*results[1] - 170.06 - 1 #recalibrate
                vbat2 = round(0.0052*results[1]+0.2293,3)
                #ibat = -0.0681*results[2] + 139.84 + 1.22 #recalibrate
                ibat = round(-0.0832*results[2]+111.74-1.08,3)
                Tbat_1 = round(-0.063*results[3] + 149.71,3)
                Tbat_2 = round(-0.0668*results[4] + 157.47,3)
                AmbTemp = round(-0.0383*results[5] + 100.5,3)
                
                #print("V_bat_1 = ", str(vbat1),"V_bat_2 = ", str(vbat2),
                #"I_bat = ", str(ibat))
                #print("T_bat_1 = ",str(Tbat_1),"T_bat_2 = ", str(Tbat_2),"T_amb",
                #str(AmbTemp),"\n")

                dt = (time.time()-tx)
                #print("dt:", round(dt,3))
        
                SoC_out=round(SoC(sd_time, dt, ibat, vbat1-vbat2),3)
                #print("SOC from esp:", SoC_out)
                
                #print("dt:", round((time.time()-tx),3))
                tx=time.time() #for SOC dt calculation


        
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
            #print('zG = ',zG)
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


        
        #each 5 seconds get the average value of temp, I, V values
        Totvbat1 = Totvbat1+vbat1
        Totvbat2 = Totvbat2+vbat2
        Totibat = Totibat+ibat
        TotTbat_1 = TotTbat_1+Tbat_1
        TotTbat_2 = TotTbat_2+Tbat_2
        TotAmbTemp = TotAmbTemp+AmbTemp
        TotSoc= TotSoc+SoC_out
        i=i+1
        jk=jk+1

        #every 1 second save in csv file
        if jk==csv_time:
            jk=0
            csv_out = [
                str(t_cpu),
                str(now),
                str(format(round(xG,3),'.3f')),
                str(format(round(yG,3),'.3f')),
                str(format(round(zG,3),'.3f')),
                str(t),
                str(h),
                str(p),
                str(format(round(acqfreq,3),'.3f')),
                vbat1,
                vbat2,
                ibat,
                Tbat_1,
                Tbat_2,
                AmbTemp,
                SoC_out
            ]
            with open(name1, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(csv_out)        
       

        #after 5 seconds write all average values in
        if i==25: #every 5 sec
            Avgvbat1 = Totvbat1/i
            Avgvbat2 = Totvbat2/i
            Avgibat = Totibat/i
            AvgTbat_1 = TotTbat_1/i
            AvgTbat_2 = TotTbat_2/i
            AvgAmbTemp = TotAmbTemp/i
            AvgSoc = TotSoc/i
            
            Totvbat1 = 0
            Totvbat2 = 0
            Totibat = 0
            TotTbat_1 = 0
            TotTbat_2 = 0
            TotAmbTemp = 0
            i=0
            TotSoc=0
            
            file1=open("WriteGUIBMS.txt","w")
            file1.write(str(format(round(Avgvbat1,3),'.3f'))+","+str(format(round(Avgvbat2,3),'.3f'))+","+str(format(round(Avgibat,3),'.3f'))+","+str(format(round(AvgTbat_1,3),'.3f'))+","+str(format(round(AvgTbat_2,3),'.3f'))+","+str(format(round(AvgAmbTemp,3),'.3f'))+","+str(format(round(AvgSoc,3),'.3f')))
            file1.close() 

        #we want a stable 5Hz operating frequency, so wait the time difference to achieve this 
        wait = gdt-time.time()+t0
        
        if wait<0:
            #print("FrequencyI2C:",1/(time.time()-t0))
            continue
        else:
            time.sleep(wait)
            #print("FrequencyI2C:",1/(time.time()-t0))
        
#######################################this function handles GPS data acquisition#######################################
def get_serial():
    """
    This function handles GPS data acquisition
    """
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
    ser = serial.Serial('/dev/ttyAMA1', 9600, timeout=5)
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
        except Exception as e:
            print(e)
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
    """
    This function runs the processes when testing the file independently
    :return:
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
         f1 = executor.submit(get_I2C)
         f2 = executor.submit(get_serial)
         #f3 = executor.submit(get_ESP)
#runProgram()
#get_ESP()
#get_I2C()
#get_serial()

