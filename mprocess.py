import time
import multiprocessing
import concurrent.futures
import csv

var1 = 0
var2 = 0
rows = [var1, var2]

# field names 
fields = ['Var1', 'Var2'] 

t1 = time.perf_counter()

def process1():
    global var1
    for i in range (5):    
        print("running process 1")
        time.sleep(1)
        var1 = i
        print(var1)
       
        
def process2():
    global var2
    for j in range (5):    
        print("running process 2")
        time.sleep(1)
        var2 = j
        print(var2)

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        
        f1 = executor.submit(process1)
        f2 = executor.submit(process2)
        print(var1)
        print(var2)
            # rows[0] = f1.result()
            # rows[1] = f2.result()
            # csvwriter.writerow(rows)
            
if __name__ == '__main__':
    main()
        
t2 = time.perf_counter()

print(f'Finished in {t2-t1} seconds')
print(var1)
print(var2)

