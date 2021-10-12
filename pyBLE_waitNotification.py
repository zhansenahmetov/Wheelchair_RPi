"""
ref:
bluepy Documentation: Working with notifications
http://ianharvey.github.io/bluepy-doc/notifications.html
"""
# Python3 example on Raspberry Pi to handle notification from
# ESP32 BLE_notify example.
#
# To install bluepy for Python3:
# $ sudo pip3 install bluepy

from bluepy import btle
import time
import struct

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        #print(cHandle)
        #print(type(data))
        print("Raw: ", data)
        str_data = data.decode("utf-8")
        print(data.decode("utf-8"))
        print(data[0])
        #print(data[1])
        #print(data[2])


# Initialisation  -------
address = "a8:03:2a:6a:43:fa"
# node 1
service_uuid = "f8470a78-beb2-4203-9f21-3e9fa4036c38"
char_uuid = "8da72fc2-bca2-4e3f-a608-ad49937a21df"

#test code       
#service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#char_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#char_uuid1 = "2f1e248e-988c-493b-a751-e0be3c63ee66"

p = btle.Peripheral(address)   #create a Peripheral object directly by specifying its MAC address
p.setDelegate(MyDelegate())    #create a delegate to process notifications

# Setup to turn notifications on, e.g.
svc = p.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics(char_uuid)[0]
#ch1 = svc.getCharacteristics(char_uuid1)[0]

print(ch)
#print(ch1)
"""
print(type(ch))
print(ch)
print(dir(ch))

peripheral = ch.peripheral
print(type(peripheral))
print(peripheral)

propNames = ch.propNames
print(type(propNames))
print(propNames)

properties = ch.properties
print(type(properties))
print(properties)
"""

"""
Remark for setup_data for bluepy noification-
Actually I don't understand how come setup_data = b"\x01\x00",
and ch.valHandle + 1.
Just follow suggestion by searching in internet:
https://stackoverflow.com/questions/32807781/
ble-subscribe-to-notification-using-gatttool-or-bluepy
"""
setup_data = b"\x01\x00"
#setup_data = b"v1= 0000 v2= 0000 v3= 0000 v4= 0000 v5= 0000 "
#ch.write(setup_data)
p.writeCharacteristic(ch.valHandle + 1, setup_data)

ch_data = p.readCharacteristic(ch.valHandle + 1)
print(type(ch_data))
print(ch_data)

print("=== Main Loop ===")

while True:
    if p.waitForNotifications(1.0):  #connection timeout is set to 1 sec
        # handleNotification() was called
        time.sleep(0.5)
        print("Inside main: ",ch.read())
        continue
    else:
        print("Still waiting for notifications!")

    #print("Waiting...")
    # Perhaps do something else here