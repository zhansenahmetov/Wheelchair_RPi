from PyQt5 import QtCore, QtGui, QtWidgets
from WHome import Ui_MainWindow #New1
from WCharging import Ui_MainWindow2 #New2
from WUpload import Ui_MainWindow4 #New4
from WTest import Ui_MainWindow3 #New3
from TimerThread import Clock
from Login_file import Login
import WCharging as wc
import main_code
import time
import concurrent.futures
import WMsgWindow as wm
import StateClass as sc
from StateClass import State
    
def showWindow(targetWindow):
#     print("attempting to change tabs, state: ",sc.WCState)
    if(sc.WCState == State.CHARGER_AVAILABLE
           or sc.WCState == State.CHARGER_UNAVAILABLE):
        winArray = [login,MainWindow,MainWindow2,MainWindow3,MainWindow4];
        winArray[targetWindow].showFullScreen();
        for idx,win in enumerate(winArray):
            if targetWindow != idx:
                win.hide()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wm.globalMsgWindow = wm.MsgWindow()
    # base state for tests
    sc.WCState = State.CHARGER_AVAILABLE
#     QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
    
    LCD_Objs = []
    # Set Up Main Windows
    MainWindow = QtWidgets.QMainWindow()
    
    # establish full screen for all windows
    login = Login()
    login.setObjectName("loga")
    login.resize(800, 480)
    MainWindow.showFullScreen() # show this in the background for seamless transition
    login.showFullScreen()
    
    # load non-active windows after to try to speedup start process
    MainWindow2 = QtWidgets.QMainWindow()
    MainWindow3 = QtWidgets.QMainWindow()
    MainWindow4 = QtWidgets.QMainWindow()
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    LCD_Objs.append(ui.lcdNumber)
    # connect goStatus method to ui of home
    #ui.label_3.clicked.connect(goBattery)
    ui.label_charging.mouseReleaseEvent = (lambda state, x=2: showWindow(x))
    
#     ui.label_3.mouseReleaseEvent = showTab(MainWindow2)
    # connect goCharge method
    #ui.label_4.clicked.connect(goTest)
    ui.label_testing.mouseReleaseEvent = (lambda state, x=4: showWindow(x))
    ui.label_upload.mouseReleaseEvent = (lambda state, x=3: showWindow(x))
#     ui.label_5.mouseReleaseEvent = showTab(MainWindow3)

    ui = Ui_MainWindow2()
    ui.setupUi(MainWindow2)
    LCD_Objs.append(ui.lcdNumber_3)
    # connect goStatus method to ui of home
    #ui.label_5.clicked.connect(goHome)
    
    ui.label_home.mouseReleaseEvent = (lambda state, x=1: showWindow(x))
    ui.label_upload.mouseReleaseEvent = (lambda state, x=3: showWindow(x))
    ui.label_testing.mouseReleaseEvent = (lambda state, x=4: showWindow(x))
#     ui.label_4.mouseReleaseEvent = showTab(MainWindow)
#     ui.label_8.mouseReleaseEvent = showTab(MainWindow3)

    ui = Ui_MainWindow4()
    ui.setupUi(MainWindow3)
    LCD_Objs.append(ui.lcdNumber)
    # connect goStatus method to ui of home
    #ui.pushButton.clicked.connect(goHome)
    
    ui.label_home.mouseReleaseEvent = (lambda state, x=1: showWindow(x))
    ui.label_charging.mouseReleaseEvent = (lambda state, x=2: showWindow(x))
    ui.label_testing.mouseReleaseEvent = (lambda state, x=4: showWindow(x))
#     ui.label_2.mouseReleaseEvent = showTab(MainWindow)
#     ui.label_3.mouseReleaseEvent = showTab(MainWindow2)

    ui = Ui_MainWindow3()
    ui.setupUi(MainWindow4)
    ui.label_home.mouseReleaseEvent = (lambda state, x=1: showWindow(x))
    ui.label_charging.mouseReleaseEvent = (lambda state, x=2: showWindow(x))
    ui.label_upload.mouseReleaseEvent = (lambda state, x=3: showWindow(x))

    if login.exec_() == QtWidgets.QDialog.Accepted:
        showWindow(1)
        # Start Clock Thread
        clock = Clock(LCD_Objs)
        clock.start()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            f1 = executor.submit(main_code.get_I2C) #BMI sensors
            f2 = executor.submit(main_code.get_serial) #gps
            #f4 = executor.submit(main_code.get_ESP) #BMS sensors
            f3 = executor.submit(sys.exit(app.exec_()))
        
        #sys.exit(app.exec_())
