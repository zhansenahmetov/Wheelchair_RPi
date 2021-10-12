import time
while True:
    t0=time.time()
    time.sleep(0.1)
    print("Frequency:",1/(time.time()-0.1-t0))