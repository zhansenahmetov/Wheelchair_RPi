from threading import Thread
from datetime import datetime
import time

class Clock(Thread):
    
    def __init__(self,lcdObjs):
        """
        lcdObj: array of lcd objects
        """
        Thread.__init__(self,name="WheelChair_Clock")
        self.starttime = datetime.now()
        self.time = self.starttime
        self.running = True
        self.LCD = lcdObjs
    
    def stop(self):
        self.running = False
    
    def getTime(self):
        return self.time
    
    # update clock every second
    def run(self):
        while self.running:
            self.time = datetime.now()
            for i in self.LCD:
                i.display(self.time.strftime("%H:%M"))
            time.sleep(1)
            
