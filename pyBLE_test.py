from bluepy import btle

MAC = "a8:03:2a:6a:43:fa"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

print("Connect to:" + MAC)
dev = btle.Peripheral(MAC)

print("\n--- dev ----------------------------")
print(type(dev))
print(dev)

print("\n--- dev.services -------------------")
for svc in dev.services:
    print(str(svc))
    
print("\n------------------------------------")
print("Get Serice By UUID: " + SERVICE_UUID)
service_uuid = btle.UUID(SERVICE_UUID)
service = dev.getServiceByUUID(service_uuid)

print(service)
print("\n--- service.getCharacteristics() ---")
print(type(service.getCharacteristics()))
print(service.getCharacteristics())

#----------------------------------------------
characteristics = dev.getCharacteristics()
print("\n--- dev.getCharacteristics() -------")
print(type(characteristics))
print(characteristics)

for char in characteristics:
    print("----------")
    print(type(char))
    print(char)
    print(char.uuid)
    if(char.uuid == CHARACTERISTIC_UUID ):
        print("=== !CHARACTERISTIC_UUID matched! ==")
        print(char)
        print(dir(char))
        print(char.getDescriptors)
        print(char.propNames)
        print(char.properties)
        print(type(char.read()))
        print(char.read())
    
#print("=== dev ============================")
#print(dir(dev))
#print("=== service ========================")
#print(dir(service))

