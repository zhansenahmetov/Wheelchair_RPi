"""
This file is responsible for maintaining the clock in the upper righthand corner of corresponding GUI tabs
"""
from threading import Thread
from datetime import datetime
import time

class Clock(Thread):
    """
    This is the class for the timer/clock
    """

    def __init__(self,lcdObjs):
        """
        This function initializes the clock

        :param lcdObjs: array of lcd objects to update with the time format
        """
        Thread.__init__(self,name="WheelChair_Clock")
        self.starttime = datetime.now()
        self.time = self.starttime
        self.running = True
        self.LCD = lcdObjs
    
    def stop(self):
        """
        This function stops the clock thread
        """
        self.running = False
    
    def getTime(self):
        """
        This function will return the current time
        """
        return self.time
    
    # update clock every second
    def run(self):
        """
        This function will run the clock thread
        """
        while self.running:
            self.time = datetime.now()
            for i in self.LCD:
                i.display(self.time.strftime("%H:%M"))
            time.sleep(1)
            
