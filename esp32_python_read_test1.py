from time import sleep
from Adafruit_PureIO.smbus import SMBus
from adafruit_extended_bus import ExtendedI2C as I2C
from Raspberry_Pi_Master_for_ESP32_I2C_SLAVE.packer import Packer
from Raspberry_Pi_Master_for_ESP32_I2C_SLAVE.unpacker import Unpacker

if "__main__" == __name__:

    try:
        i2c = I2C(1)
        scan = i2c.scan()
        print("I2c devices found: ", scan)
        with SMBus(1) as smbus:
            address = scan[0]
            register = [244, 128, 2, 3]
            num_of_bytes = 5
            unpacked = None
            with Packer() as packer:
                packer.debug = True
                packer.write(register[0])
                packer.end()
                packed = packer.read()
                print("packed: ", packed)
            smbus.write_bytes(address, bytearray(packed))
            sleep(0.8)  # let the bus process first write
            raw = smbus.read_bytes(address, num_of_bytes)
            with Unpacker() as unpacker:
                unpacker.debug = True
                unpacker.write(list(raw))
                unpacked = unpacker.read()
            print("This is unpacked = ", unpacked)
    except Exception as e:
        print("ERROR: {}".format(e))