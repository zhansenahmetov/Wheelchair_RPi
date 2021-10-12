import smbus
bus = smbus.SMBus(1)
from LSM6DSL import *
from LIS3MDL import *
import time


def writeByte(device_address,register,value):
    bus.write_byte_data(device_address, register, value)


def readACCx():
    acc_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTX_L_XL)
    acc_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTX_H_XL)

    acc_combined = (acc_l | acc_h <<8)
    return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCy():
    acc_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTY_L_XL)
    acc_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTY_H_XL)

    acc_combined = (acc_l | acc_h <<8)
    return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCz():
    acc_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTZ_L_XL)
    acc_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTZ_H_XL)

    acc_combined = (acc_l | acc_h <<8)
    return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readGYRx():
    gyr_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTX_L_G)
    gyr_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTX_H_G)

    gyr_combined = (gyr_l | gyr_h <<8)
    return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536


def readGYRy():
    gyr_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTY_L_G)
    gyr_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTY_H_G)

    gyr_combined = (gyr_l | gyr_h <<8)
    return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
    gyr_l = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTZ_L_G)
    gyr_h = bus.read_byte_data(LSM6DSL_ADDRESS, LSM6DSL_OUTZ_H_G)

    gyr_combined = (gyr_l | gyr_h <<8)
    return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536


def readMAGx():
    mag_l = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_X_L)
    mag_h = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_X_H)

    mag_combined = (mag_l | mag_h <<8)
    return mag_combined  if mag_combined < 32768 else mag_combined - 65536


def readMAGy():
    mag_l = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_Y_L)
    mag_h = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_Y_H)

    mag_combined = (mag_l | mag_h <<8)
    return mag_combined  if mag_combined < 32768 else mag_combined - 65536


def readMAGz():
    mag_l = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_Z_L)
    mag_h = bus.read_byte_data(LIS3MDL_ADDRESS, LIS3MDL_OUT_Z_H)

    mag_combined = (mag_l | mag_h <<8)
    return mag_combined  if mag_combined < 32768 else mag_combined - 65536


def initIMU():
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b00111111)           #ODR 52 Hz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01001111)           #ODR 104 Hz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01011111)           #ODR 208 Hz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01101111)           #ODR 416 Hz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01111111)           #ODR 833 Hz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b10001111)           #ODR 1.66 kHz, +/- 8g , BW = 400hz
    writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b10011111)           #ODR 3.33 kHz, +/- 8g , BW = 400hz
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL8_XL,0b11001000)           #Low pass filter enabled, BW9, composite filter
    writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL3_C,0b01000100)            #Enable Block Data update, increment during multi byte read

    #initialise the gyroscope
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b00111100)            #ODR 52 Hz, 2000 dps
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b01001100)            #ODR 104 Hz, 2000 dps
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b01011100)            #ODR 208 Hz, 2000 dps
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b01101100)            #ODR 416 Hz, 2000 dps
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b01111100)            #ODR 833 Hz, 2000 dps
    #writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b10001100)            #ODR 1.66 kHz, 2000 dps
    writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL2_G,0b10011100)            #ODR 3.33 kHz, 2000 dps

    #initialise the magnetometer
    writeByte(LIS3MDL_ADDRESS,LIS3MDL_CTRL_REG1, 0b11011100)         # Temp sesnor enabled, High performance, ODR 80 Hz, FAST ODR disabled and Selft test disabled.
    writeByte(LIS3MDL_ADDRESS,LIS3MDL_CTRL_REG2, 0b00100000)         # +/- 8 gauss
    writeByte(LIS3MDL_ADDRESS,LIS3MDL_CTRL_REG3, 0b00000000)         # Continuous-conversion mode

