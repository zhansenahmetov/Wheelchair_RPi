import io
import pynmea2
import serial
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=0.1)

while True:
    try:
        t0 = time.time()
        line = ser.readline().decode()
        if line.startswith("$GNGGA"):
            msg = pynmea2.parse(line)
            #print(msg.latitude)
            #print(msg.lat_dir)
            #print(msg.longitude)
            #print(msg.lon_dir)
            #print(msg.num_sats)
            #print(msg.timestamp)
            lat = msg.latitude
            latd = msg.lat_dir
            lon = msg.longitude
            lond = msg.lon_dir
            numsat = msg.num_sats
            GPStime = msg.timestamp
        elif line.startswith("$GNVTG"):
            msg = pynmea2.parse(line)
            index=0
            numComma=0
            while numComma<8:
                if line[index]==",":
                    numComma=numComma+1
                    if numComma==7:
                        startind = 1+index
                    elif numComma==8:
                        endind = index
                index=index+1
            speed = line[startind:endind]
            #print(speed)
        print("Frequency:",1/(time.time()-t0))
    except:
        print("GPS error!")

    
