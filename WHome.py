"""
This file is responsible for creating the Home page of the Wheelchair GUI
"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Window_col_new.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from threading import Thread
import time
import QT_Helpers as qt_helper

class Ui_MainWindow(object):
    """
    This class creates the main window that is used as the Home 'tab'
    """
    def setupUi(self, MainWindow):
        """
        This function will set up the UI elements that will be present on this window

        :param MainWindow: the window on which to build the elements
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_pic1 = QtWidgets.QLabel(self.centralwidget)
        self.label_pic1.setGeometry(QtCore.QRect(20, 320, 200, 100))
        self.label_pic1.setText("")
        self.label_pic1.setObjectName("label_pic1")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(150, 90, 471, 151))
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(690, 0, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setProperty("value", 12.0)
        self.lcdNumber.display("88:88")
#         self.lcdNumber.setProperty("intValue", 12)
        self.lcdNumber.setObjectName("lcdNumber")
        
        # Tab Navigation
        self.label_home = qt_helper.makeTabLabel(self,0,0,161,71,202,21,"label_home","Home")
        self.label_charging = qt_helper.makeTabLabel(self,163,0,161,71,152,21,"label_charging","Charging")
        self.label_upload = qt_helper.makeTabLabel(self,326,0,161,71,152,21,"label_charging","Upload")
        self.label_testing = qt_helper.makeTabLabel(self,489,0,161,71,152,21,"label_testing","Test Page")

        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(300, 290, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(300, 330, 181, 81))
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
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        
        #loading image
        self.pixmap = QPixmap('ncpic.jpg')
        self.pixmap = self.pixmap.scaledToWidth(180)
        
        self.label_pic1.setPixmap(self.pixmap)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        This function retranslates the text content of some components

        :param MainWindow: parent window of the target components
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "WELCOME, JOHN DOE!"))
        self.label_6.setText(_translate("MainWindow", "Battery Level"))
        t = Thread(target = self._readParam)
        t.start()
        
    def _readParam(self):
        """
        This function will update the battery icon using the BMS values
        """

        while True:
            
            f = open("WriteGUIBMS.txt","r")
            listOfData = f.read().split(',')
            f.close()
            
            #Battery (now SoC)
            num3 = float(listOfData[6])
            num3 = int(num3)
            self.progressBar.setProperty("value", num3)
            time.sleep(5)
            

if __name__ == "__main__":
    """
    This statement is for testing this file independently
    """
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
