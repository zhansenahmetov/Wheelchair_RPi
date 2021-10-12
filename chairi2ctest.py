import smbus
import time
import sys

temp = [0 for k in range(10)]
result = [0 for k in range(5)]
BMS_catch = ""

bus = smbus.SMBus(1)

address = 0x75

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte_data(address,1)
    return number

print("ready")
while True:

    #data = input("Input command")

    #if data == "catch":
    BMS_control = input("Receive from BMS >>> HOLD Enter!")
    if(BMS_control == ""):
        try:
            #send command to BMS to initiat data transmission
            writeNumber(12)
            for i in range(10):
                temp[i] = readNumber()
        except:
            print("BMS is disconnected!")
#     else:
#         print("Input 1 to catch data...")
        
        
    j = [0,1]
    
    for k in range(5):
        result[k] = (temp[j[1]] << 8)+temp[j[0]]
        j[0] = j[0] + 2
        j[1] = j[1] + 2
        
    vbat = 0.0803*result[0]-165.68
    ibat = -0.0681*result[1] + 139.84
    
    print("V_battery = %.2d, I_battery = %.2f" % (vbat, ibat))
    
    #elif data == "arm":
        #print("OK")
    #elif data == "disarm":
        #print("OK")

