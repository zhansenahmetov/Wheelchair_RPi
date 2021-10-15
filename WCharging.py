"""
This file is responsible for creating the Charging page of the Wheelchair's GUI
"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Window2_col_new.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from threading import Thread
#Bluetooth
from bluedot.btcomm import BluetoothClient
import time
import QT_Helpers as qt_helper
import WMsgWindow as wm
from StateClass import State
import StateClass as sc

bd_addr = "E4:5F:01:41:4D:EA"


listB = []
#IV char of battery
Inom=9
Vnom=25
StringStyle="border-top-left-radius: 35px;\n border-top-right-radius : 35px;\n border-bottom-left-radius :35px;\n border-bottom-right-radius :35px;"

class Ui_MainWindow2(object):
    """
    This class creates the main window that is used as the Charging 'tab'
    """
    global listB, Inom, Vnom

    def data_received(data):
        """
        This function interprets data received over bluetooth connection from the Raspberry Pi on the Charger's side

        :param data: numeral instruction corresponding to the established communication lookup table
        """
        print(data)
        #tC.join()
        #listB[2].join()
        time.sleep(1)
        print(listB[1])
        
        
        # connected confirmation
        if(int(data)==1 and sc.WCState == State.CONNECTING_TO_CHARGER):
            listB[1].setState(State.CONNECTED_TO_CHARGER)
            
        # charger is busy
        if(int(data)==2 and sc.WCState == State.CONNECTING_TO_CHARGER):
            listB[1].setState(State.CHARGER_AVAILABLE)
        
        #charger is disconnected
        if(int(data)==2):
            listB[1].setState(State.CHARGER_AVAILABLE)
            
        # charger denies request
        if(int(data)==4 and sc.WCState == State.REQUESTED):
            wm.globalMsgWindow.showMsg(duration=3,title="Warning",text='Charging request has been denied!',callback=[listB[1].setState,State.CHARGER_INCOMPATIBLE])
            
        # charger is waiting for connection
        if(int(data)==5 and sc.WCState == State.REQUESTED):
            listB[1].setState(State.AWAITING_CONNECTION)
            
        # charger accepts request and is ready to start
        if(int(data)==6 and (sc.WCState == State.AWAITING_CONNECTION or sc.WCState == State.REQUESTED )):
                wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='Charger is connected and ready',callback=[listB[1].setState,State.READY_TO_CHARGE])
           
        # charging has been started
        if int(data)==7 and sc.WCState == State.STARTING_CHARGE:
#             print('sent??')
            time.sleep(1)   # wait period to stop spamming of stop/start
            wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='Charging successfully started.')
            listB[1].setState(State.CHARGING_IN_PROGRESS)
        
        # there is an error with the charger side
        if(int(data)==8):
            listB[1].setState(State.CHARGER_FAULTY)
        
        # Wheelchair is fully charged
        if(int(data)==9):
            listB[1].setState(State.WC_FULLY_CHARGED)
        
        # There is an error with the battery side
        if(int(data)==10):
            listB[1].setState(State.BATTERY_FAULTY)
            
        # charging confirmation stopped by user
        if int(data)==11:
#             print(data)
            wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='Charging Stopped.',callback=[listB[1].setState,State.READY_TO_CHARGE])    
        
        if(int(data)==12):
            wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='Charger has malfunctioned.',callback=[listB[1].setState,State.CHARGER_AVAILABLE])        
        
        # Battery has been disconncted
        if(int(data)==14):
            wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='Charger has been unplugged by the user!',callback=[listB[1].DisconnectFromCharger,None])
            
    def connect_BLU(self,c):
        """
        This function will attempt to initiate a bluetooth connection

        :param c: Object reference on which to create a bluetooth connection
        """
        
        c.connect()
        
        # delay to clear queue'd mouseevents
        qt_helper.DelayAction(0.1,[self.setState,State.CONNECTED_TO_CHARGER]).start()
        
    def disconnect_BLU(self,c):
        """
        This function will terminate a bluetooth connection

        :param c: Object reference with an active bluetooth connection
        """
        c.disconnect()
        # delay to clear queue'd mouseevents
        qt_helper.DelayAction(1,[self.setState,State.CHARGER_AVAILABLE]).start()
        
    def send_BLU(self,c,data):
        """
        This function will send data over an active bluetooth connection

        :param c: Object reference with an active bluetooth connection
        :param data: Data to send over the connection
        """
        c.send(data)
    
    c = BluetoothClient(bd_addr,data_received, auto_connect=False)
    listB.append(c)

    def stateUpdate(self):
        """
        This function is the 'brains' of the state machine on the Wheelchair side.  Each time it is called it updates the
        relevent GUI components corresponding to the active state as defined by :obj:`StateClass.State`
        """
        # Defaults (QT will update after function corrects these):
#         self.label_connect.setText("Disconnect")
#         self.label_start.setText("Start Charging")
        if(sc.WCState == State.CHARGER_UNAVAILABLE):
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Disconnected")
            self.label_c_nearby.setText("No Charger Nearby")
            self.label_connect.setText("Request Charging")
            
        elif(sc.WCState == State.CHARGER_AVAILABLE):
            self.setGreen(self.label_connect)
            self.setGrey(self.label_start)
            self.label_status.setText("Disconnected")
            # hard coded for prototype, in future this should be detected
            self.label_c_nearby.setText("Charger #1 (Centennial)")
            self.label_connect.setText("Request Charging")
            
        elif(sc.WCState == State.CONNECTING_TO_CHARGER):  # after connect (before response)
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Connecting...")
            self.label_connect.setText("Disconnect")
            
        elif(sc.WCState == State.CONNECTED_TO_CHARGER):  # after connect
            self.setRed(self.label_connect)
            self.setGrey(self.label_start)
#             self.label_status.setText("Connected to Charger")
            self.RequestCharging()
            
        elif(sc.WCState == State.REQUESTED):
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Requesting Charging...")
            
        elif(sc.WCState == State.CHARGER_INCOMPATIBLE):  # after request (before accepted?)
            self.setRed(self.label_connect)
            self.setGrey(self.label_start)
            self.label_status.setText("Incompatible with Charger")
#             
#         elif(sc.WCState == State.CHARGER_COMPATIBLE):  # after request (after accepted?)
#             self.setRed(self.label_connect)
#             self.setGrey(self.label_start)
#             self.label_status.setText("Compatible with Charger!")
#             # transition after 1 second here
#             qt_helper.DelayAction(2,[self.setState,State.AWAITING_CONNECTION]).start()
            
        elif(sc.WCState == State.AWAITING_CONNECTION):  # not sure how this differs from CHARGER_COMPATIBLE
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Please plug in the battery")
            # transition after 3 seconds here, to simulate plugging power
            wm.globalMsgWindow.showMsg(duration=5,title="Instruction",text='Please connect the power now.')
            
        elif(sc.WCState == State.READY_TO_CHARGE):  # enables the start button
            wm.globalMsgWindow.hide()
            self.setGrey(self.label_connect)
            self.setGreen(self.label_start)
            self.label_status.setText("Ready to charge! (or unplug)")
            self.label_start.setText("Start Charging")
            
        elif(sc.WCState == State.STARTING_CHARGE):
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Sending start command...")
            self.label_start.setText("Stop Charging")
            
        elif(sc.WCState == State.CHARGING_IN_PROGRESS):
            self.setGrey(self.label_connect)
            self.setRed(self.label_start)
            self.label_status.setText("Charging in progress")
            self.label_start.setText("Stop Charging")
            
        elif(sc.WCState == State.CHARGER_FAULTY):
            self.setGrey(self.label_connect,self.label_start)
            wm.globalMsgWindow.showMsg(duration=3,title="Warning",text='There is an error with the charger!',callback=[self.setState,State.AWAITING_DISCONNECTION])
        
        elif(sc.WCState == State.BATTERY_FAULTY):
            self.setGrey(self.label_connect,self.label_start)
            wm.globalMsgWindow.showMsg(duration=3,title="Warning",text='The wheelchair battery is faulty!',callback=[self.setState,State.AWAITING_DISCONNECTION])
        
        elif(sc.WCState == State.TERMINATED_BY_USER):
            # buttons disabled while charger receives stop request
            self.label_status.setText("Sending termination command...")
            self.setGrey(self.label_connect,self.label_start)
            # message here will be initiated from bluetooth
        elif(sc.WCState == State.WC_FULLY_CHARGED):
            # buttons disabled while message is displayed
            self.setGrey(self.label_connect,self.label_start)
            wm.globalMsgWindow.showMsg(duration=3,title="Informational Message",text='The battery is fully charged!',callback=[self.setState,State.AWAITING_DISCONNECTION])
        
        elif(sc.WCState == State.AWAITING_DISCONNECTION): 
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Please Unplug the Battery")
            # transition after 3 seconds here, to simulate disconnecting power
#             wm.globalMsgWindow.showMsg(duration=3,title="Instruction",text='Please Disconnect the power now.',callback=[self.setState,State.CONNECTED_TO_CHARGER])
        
        elif(sc.WCState == State.DISCONNECTING):
            self.setGrey(self.label_connect,self.label_start)
            self.label_status.setText("Disconnecting...")
            
        self.label_connect.update()
        self.label_start.update()
        self.label_status.update()
        self.label_connect.hide()
        self.label_connect.show()
        self.label_start.hide()
        self.label_start.show()
        self.label_status.hide()
        self.label_status.show()
        QtWidgets.qApp.processEvents()

    def setState(self,state=State.CHARGER_UNAVAILABLE):
        """
        This function sets the state of the Wheelchair and updates components using :obj:`WCharging.Ui_MainWindow2.stateUpdate`

        :param state: The state which the Wheelchair will be set to, available options defined in :obj:`StateClass.State`
        """
        sc.WCState = state
#         qt_helper.DelayAction(0.5,[self.stateUpdate,None]).start()
        self.stateUpdate()

    def setGreen(self,*objs):
        """
        This function will change the color of provided objects to green (rgb: 0, 130, 0), using :obj:`WCharging.Ui_MainWindow2.setColor`

        :param objs: objects to change the color of
        """
        self.setColor(0,130,0,*objs)
        
    def setRed(self,*objs):
        """
        This function will change the color of provided objects to red (rgb: 222, 0, 0), using :obj:`WCharging.Ui_MainWindow2.setColor`

        :param objs: objects to change the color of
        """
        self.setColor(222,0,0,*objs)
        
    def setGrey(self,*objs):
        """
        This function will change the color of provided objects to Grey (rgb: 202, 202, 202), using :obj:`WCharging.Ui_MainWindow2.setColor`

        :param objs: objects to change the color of
        """
        self.setColor(202,202,202,*objs)
            
    def setColor(self,r,g,b,*objs):
        """
        This function will change the color of provided objects, given the rgb values

        :param r: rgb value for red
        :param g: rgb value for green
        :param b: rgb value for blue
        :param objs: objects to change the color of
        """
        for i in objs:
            i.setStyleSheet("QLabel {background-color: rgb("+str(r)+", "+str(g)+", "+str(b)+");\n"
        "color: rgb(255, 255, 255);"+StringStyle+"}")

    def setupUi(self, MainWindow2):
        """
        This function will set up the UI elements that will be present on this window

        :param MainWindow2: the window on which to build the elements
        """
        MainWindow2.setObjectName("MainWindow2")
        MainWindow2.resize(800, 480)
        listB.append(self)
        self.centralwidget = QtWidgets.QWidget(MainWindow2)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(620, 120, 171, 81))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.progressBar.setFont(font)
        self.progressBar.setStyleSheet("")
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        #Make it green and align to center
        self.progressBar.setStyleSheet("QProgressBar::chunk"
                                       "{"
                                       "background-color: rgb(0,205,0);"
                                       "}")
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        #End of progress bar settings
        
        # Tab Navigation
        self.label_home = qt_helper.makeTabLabel(self,0,0,161,71,152,21,"label_home","Home")
        self.label_charging = qt_helper.makeTabLabel(self,163,0,161,71,202,21,"label_charging","Charging")
        self.label_upload = qt_helper.makeTabLabel(self,326,0,161,71,152,21,"label_charging","Upload")
        self.label_testing = qt_helper.makeTabLabel(self,489,0,161,71,152,21,"label_testing","Test Page")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(620, 80, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(620, 230, 131, 51))
        self.lcdNumber.setObjectName("lcdNumber")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(620, 210, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.lcdNumber_2 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber_2.setGeometry(QtCore.QRect(620, 310, 131, 51))
        self.lcdNumber_2.setObjectName("lcdNumber_2")
#         self.label_request = QtWidgets.QLabel(self.centralwidget)
#         self.label_request.setGeometry(QtCore.QRect(190, 340, 171, 71))
#         font = QtGui.QFont()
#         font.setPointSize(15)
#         self.label_request.setFont(font)
#         self.label_request.setLayoutDirection(QtCore.Qt.LeftToRight)
#         self.label_request.setStyleSheet("\n"
# "background-color: rgb(202, 202, 202);\n"
# "color: rgb(255, 255, 255);\n"
# "border-top-left-radius: 35px;\n"
# "border-top-right-radius : 35px;\n"
# "border-bottom-left-radius :35px;\n"
# "border-bottom-right-radius :35px;")
#         self.label_request.setFrameShape(QtWidgets.QFrame.NoFrame)
#         self.label_request.setAlignment(QtCore.Qt.AlignCenter)
#         self.label_request.setObjectName("label_request")
        self.label_start = QtWidgets.QLabel(self.centralwidget)
        self.label_start.setGeometry(QtCore.QRect(310, 340, 230, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_start.setFont(font)
        self.label_start.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_start.setStyleSheet("background-color: rgb(202, 202, 202);\n"
"color: rgb(255, 255, 255);\n"
"border-top-left-radius: 35px;\n"
"border-top-right-radius : 35px;\n"
"border-bottom-left-radius :35px;\n"
"border-bottom-right-radius :35px;")
        self.label_start.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_start.setAlignment(QtCore.Qt.AlignCenter)
        self.label_start.setObjectName("label_start")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(10, 130, 150, 51))
#         self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(620, 290, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_connect = QtWidgets.QLabel(self.centralwidget)
        self.label_connect.setGeometry(QtCore.QRect(40, 340, 230, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_connect.setFont(font)
        self.label_connect.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_connect.setStyleSheet("background-color: rgb(0, 130, 0);\n"
"color: rgb(255, 255, 255);\n"
"border-top-left-radius: 35px;\n"
"border-top-right-radius : 35px;\n"
"border-bottom-left-radius :35px;\n"
"border-bottom-right-radius :35px;")
        self.label_connect.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_connect.setAlignment(QtCore.Qt.AlignCenter)
        self.label_connect.setObjectName("label_connect")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(5, 125, 551, 61))
        self.frame.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(4)
        self.frame.setObjectName("frame")
        self.lcdNumber_3 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber_3.setGeometry(QtCore.QRect(690, 0, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.lcdNumber_3.setFont(font)
        self.lcdNumber_3.setProperty("value", 12.0)
        self.lcdNumber_3.setProperty("intValue", 12)
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(10, 200, 150, 51))
#         self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.label_status = QtWidgets.QLabel(self.centralwidget)
        self.label_status.setGeometry(QtCore.QRect(160, 200, 400, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_status.setFont(font)
        self.label_status.setObjectName("label_11")
        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.label_c_nearby = QtWidgets.QLabel(self.centralwidget)
        self.label_c_nearby.setGeometry(QtCore.QRect(160, 130, 400, 51))
        self.label_c_nearby.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_c_nearby.setFont(font)
        self.label_c_nearby.setObjectName("label_15")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(5, 200, 551, 61))
        self.frame_2.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setLineWidth(4)
        self.frame_2.setObjectName("frame_2")

        MainWindow2.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow2)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow2.setMenuBar(self.menubar)
        
        
        
        
        #create message box
        self.msg = QMessageBox()
        # Set the information icon
        self.msg.setIcon(QMessageBox.Information)
        # Set the main message
        self.msg.setText("Successfully connected to charger")
        # Set the title of the window
#         self.msg.setWindowTitle("Informational Message")
        
        #create message box
        self.msg1 = QMessageBox()
        # Set the information icon
        self.msg1.setIcon(QMessageBox.Information)
        # Set the main message
        self.msg1.setText("Charger is not available now")
        # Set the title of the window
        self.msg1.setWindowTitle("Informational Message")
        #         #create message box
        self.msg5 = QMessageBox()
#         # Set the information icon
        self.msg5.setIcon(QMessageBox.Information)
#         # Set the main message
        self.msg5.setText("Charging stopped")
#         # Set the title of the window
        self.msg5.setWindowTitle("Informational Message")
#         self.msg2 = qt_helper.makeMsgBox(title="Informational Message",text="Charging request has been accepted")
        self.msg4 = QMessageBox()
#         # Set the information icon
        self.msg4.setIcon(QMessageBox.Information)
#         # Set the main message
        self.msg4.setText("Charging started")
#         # Set the title of the window
        self.msg4.setWindowTitle("Informational Message")

        #Three buttons function declaration
#         self.label_request.mouseReleaseEvent = self.RequestCharging
        self.label_start.mouseReleaseEvent = self.StartStopCharge
        self.label_connect.mouseReleaseEvent = self.ConnectToCharger
        
        self.retranslateUi(MainWindow2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow2)

    def retranslateUi(self, MainWindow2):
        """
        This function will reassign some components' textual content

        :param MainWindow2: parent window of the target components
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow2.setWindowTitle(_translate("MainWindow2", "MainWindow"))
        self.label.setText(_translate("MainWindow2", "Battery Level"))
        self.label_2.setText(_translate("MainWindow2", "Battery 1 temp (C)"))
#         self.label_request.setText(_translate("MainWindow2", "Request Charging"))
        self.label_start.setText(_translate("MainWindow2", "Start Charging"))
        self.label_9.setText(_translate("MainWindow2", "Charger nearby:"))
        self.label_3.setText(_translate("MainWindow2", "Battery 2 temp (C)"))
        self.label_connect.setText(_translate("MainWindow2", "Request Charging"))
        self.label_10.setText(_translate("MainWindow2", "Status:"))
        self.label_status.setText(_translate("MainWindow2", "Disconnected"))
        self.label_c_nearby.setText(_translate("MainWindow2", "Charger #1 (Centennial)"))
        
        t = Thread(target = self._readParam)
        t.start()
        
    def _readParam(self):
        """
        This function will read the BMS Voltage and Current values from the data file then update the corresponding LCD elements and battery icon
        """
        V = 0
        I = 100
        while True:
            
            f = open("WriteGUIBMS.txt","r")
            listOfData = f.read().split(',')
            f.close()
            #Temperature 1 and 2 of battery
            num1 = float(listOfData[3])
            num1 = int(num1)
            num2 = float(listOfData[4])
            num2 = int(num2)
            
            self.lcdNumber.display(num1)
            self.lcdNumber_2.display(num2)
            #Battery (now SoC)
            num3 = float(listOfData[6])
            num3 = int(num3)
            self.progressBar.setProperty("value", num3)
            time.sleep(5)
        
    def StartStopCharge(self,event=None):
        """
        This function will Start or stop charging depending on the current state (this function is directly linked to the start/stop button)

        :param event: unused parameter that may be sent when initiated from a button call
        """
        # Start Charging
        if sc.WCState == State.READY_TO_CHARGE:
            print("start")
            self.setState(State.STARTING_CHARGE)
            data="7,"+str(Inom)+","+str(Vnom)
            self.send_BLU(listB[0],data)
        # Stop Charging
        elif sc.WCState == State.CHARGING_IN_PROGRESS:
            print("stop")
            data="11,"+str(Inom)+","+str(Vnom)
            self.setState(State.TERMINATED_BY_USER)  
            self.send_BLU(listB[0],data)
        
    def ConnectToCharger(self, event=None):
        """
        This function will initiate a connection or disconnect from the charger depending on the current state (this function is directly linked to the connect/disconnect button)

        :param event: unused parameter that may be sent when initiated from a button call
        """
#         print("connect clicked ",sc.WCState)
        if sc.WCState == State.CHARGER_AVAILABLE:
            self.setState(State.CONNECTING_TO_CHARGER)
            try:
                tC = Thread(target = self.connect_BLU(listB[0]))
                #listB.append(tC)
                tC.start()
            except Exception as e:
                # delay to clear queue'd mouseevents
                qt_helper.DelayAction(0.1,[self.setState,State.CHARGER_AVAILABLE]).start()
#                 self.setState(State.CHARGER_AVAILABLE)
                print("Charger Connection Error:",e)

        # can only disconnect in safe states
        elif sc.WCState == State.CONNECTED_TO_CHARGER \
            or sc.WCState == State.CHARGER_INCOMPATIBLE:
            self.DisconnectFromCharger()
            
    def DisconnectFromCharger(self):
        """
        This function will disconnect the Wheelchair from the Charger (may be internally executed from bluetooth instruction in :obj:`WCharging.Ui_MainWindow2.data_received`
        """
        self.setState(State.DISCONNECTING)
        try:
            self.disconnect_BLU(listB[0])
        except Exception as e:
            print("disconnection error: ",e)
            qt_helper.DelayAction(1,[self.setState,State.CHARGER_AVAILABLE]).start()
#             self.setState(State.CHARGER_AVAILABLE)
    
    def RequestCharging(self):
        """
        This function will request charging from the charger given it is in the connected state
        """
        try:
            if sc.WCState == State.CONNECTED_TO_CHARGER:
                # delay to clear queue'd mouseevents
                self.setState(State.REQUESTED)
                data="3,"+str(Inom)+","+str(Vnom)
                self.send_BLU(listB[0],data)
                print("requested")
        except Exception as e:
            print("Error while sending request:",e)

if __name__ == "__main__":
    """
    This statement is for testing the file independently
    """
    import sys
    # base state
    sc.WCState = State.CHARGER_AVAILABLE
    app = QtWidgets.QApplication(sys.argv)
    wm.globalMsgWindow = wm.MsgWindow()
    MainWindow2 = QtWidgets.QMainWindow()
    ui = Ui_MainWindow2()
    ui.setupUi(MainWindow2)
    MainWindow2.showFullScreen()
    sys.exit(app.exec_())
