import smbus
import time

#select I2C bus1 on the Pi, give address for BMS (75)
bus = smbus.SMBus(1)
address = 0x60

#bus.write_byte(address, 0x0)
k = 1
while True:
    
    try:
        #sends command to BMS to initiate data transmission
        bus.write_byte(address, k)
        MSG = bus.read_byte_data(address,0)
        print(MSG)
        time.sleep(1)
    #     for i in range(10):
    #         MSG[i] = bus.read_byte_data(address,1)
    except:
        print("BMS Error!")
        time.sleep(1)
  
        
    

#
# from time import sleep
# from Adafruit_PureIO.smbus import SMBus
# from adafruit_extended_bus import ExtendedI2C as I2C
# 
# if "__main__" == __name__:
# 
#     try:
#         i2c = I2C(1)
#         scan = i2c.scan()
#         print("I2c devices found: ", scan)
#         with SMBus(1) as smbus:
#             address = scan[0]
#             register = [244, 128, 2, 3]
#             num_of_bytes = 5
#             unpacked = None
#             with Packer() as packer:
#                 packer.debug = True
#                 packer.write(register[0])
#                 packer.end()
#                 packed = packer.read()
#                 print("packed: ", packed)
#             smbus.write_bytes(address, bytearray(packed))
#             sleep(0.8)  # let the bus process first write
#             raw = smbus.read_bytes(address, num_of_bytes)
#             with Unpacker() as unpacker:
#                 unpacker.debug = True
#                 unpacker.write(list(raw))
#                 unpacked = unpacker.read()
#             print(unpacked)
#     except Exception as e:
#         print("ERROR: {}".format(e))