"""
This file is responsible for creating the login page of the Wheelchair GUI
"""
from PyQt5 import QtCore, QtGui, QtWidgets

import os
import sys
import QT_Helpers as qt_helper
import WMsgWindow as wm

# os.environ["QT_DIR"] = "/home/pi/qt/5.11.3/gcc_64"
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/home/pi/qt/5.11.3/gcc_64/plugins/platforms"
# os.environ["QT_PLUGIN_PATH"] = "/home/pi/qt/5.11.3/gcc_64/plugins"
# os.environ["QML_IMPORT_PATH"] = "/home/pi/qt/5.11.3/gcc_64/qml"
# #os.environ["QML2_IMPORT_PATH"] = "/home/pi/qt/5.11.3/gcc_64/qml"
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# from mainwindow import Ui_MainWindow

class Login(QtWidgets.QDialog):
    """
    This class creates the login dialog to precede the other GUI pages
    """
    def __init__(self, parent=None):
        """
        This function will initialized the login page

        :param parent: the parent upon which to establish the login page
        """
        super(Login, self).__init__(parent)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(280, 15, 240, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
#         self.lineEdit_2 = QtWidgets.QLineEdit(self)
#         self.lineEdit_2.setGeometry(QtCore.QRect(140, 130, 241, 61))
#         font = QtGui.QFont()
#         font.setPointSize(14)
#         self.lineEdit_2.setFont(font)
#         self.lineEdit_2.setObjectName("lineEdit_2")        
        
        # Login / Cancel Buttons
#         self.loginButton = qt_helper.makeButton(self,440,110,151,81,16,"pushButton","Login")
#         self.cancelButton = qt_helper.makeButton(self,630,110,151,81,16,"pushButton_2","Cancel")
        
        # PIN Pad creation
        
        # Buttons 1-9
        self.pinPadButtons = []
        pinButtonSize = 80
        pinX = 280 # top left coords
        pinY = 90 # top left coords
        pinX_ = 80 # horizontal spacing
        pinY_ = 80 # vertical spacing
        
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+pinX_,pinY+3*pinY_,pinButtonSize,pinButtonSize,14,'Pin0','0'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX,pinY+2*pinY_,pinButtonSize,pinButtonSize,14,'Pin1','1'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+pinX_,pinY+2*pinY_,pinButtonSize,pinButtonSize,14,'Pin2','2'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+2*pinX_,pinY+2*pinY_,pinButtonSize,pinButtonSize,14,'Pin3','3'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX,pinY+1*pinY_,pinButtonSize,pinButtonSize,14,'Pin4','4'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+pinX_,pinY+1*pinY_,pinButtonSize,pinButtonSize,14,'Pin5','5'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+2*pinX_,pinY+1*pinY_,pinButtonSize,pinButtonSize,14,'Pin6','6'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX,pinY,pinButtonSize,pinButtonSize,14,'Pin7','7'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+pinX_,pinY,pinButtonSize,pinButtonSize,14,'Pin8','8'))
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+2*pinX_,pinY,pinButtonSize,pinButtonSize,14,'Pin9','9'))
        
        for idx,btn in enumerate(self.pinPadButtons):
            btn.clicked.connect(lambda state, x=idx: self.enterPin(x))
            
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX+2*pinX_,pinY+3*pinY_,pinButtonSize,pinButtonSize,14,'PinRet','Enter'))
        self.pinPadButtons[-1].clicked.connect(self.handleLogin)
        self.pinPadButtons.append(qt_helper.makeButton(self,pinX,pinY+3*pinY_,pinButtonSize,pinButtonSize,14,'PinClr','Clear'))
        self.pinPadButtons[-1].clicked.connect(self.clearPin)
        
        # End of PIN Pad Creation
        
#         self.label_2 = QtWidgets.QLabel(self)
#         self.label_2.setGeometry(QtCore.QRect(20, 140, 111, 31))
#         font = QtGui.QFont()
#         font.setPointSize(15)
#         self.label_2.setFont(font)
#         self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(220, 45, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self)
        self.commandLinkButton.setGeometry(QtCore.QRect(220, 420, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.commandLinkButton.setFont(font)
        self.commandLinkButton.setIconSize(QtCore.QSize(25, 30))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.commandLinkButton_2 = QtWidgets.QCommandLinkButton(self)
        self.commandLinkButton_2.setGeometry(QtCore.QRect(380, 420, 191, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.commandLinkButton_2.setFont(font)
        self.commandLinkButton_2.setIconSize(QtCore.QSize(25, 30))
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")

        #commands
#         self.loginButton.clicked.connect(self.handleLogin)
        self.commandLinkButton.clicked.connect(self.registration)

        self.retranslateUi()
    
    def retranslateUi(self):
        """
        
        :return:
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Login Page"))
        self.lineEdit.setPlaceholderText(_translate("Dialog", "PIN Number"))
#         self.lineEdit_2.setPlaceholderText(_translate("Dialog", "Password"))
#         self.loginButton.setText(_translate("Dialog", "Login"))
#         self.cancelButton.setText(_translate("Dialog", "Cancel"))
#         self.label_2.setText(_translate("Dialog", "Password"))
        self.label_3.setText(_translate("Dialog", "PIN:"))
        self.commandLinkButton.setText(_translate("Dialog", "Registration"))
        self.commandLinkButton_2.setText(_translate("Dialog", "Forgot password"))
        
        
    def enterPin(self,n):
        self.lineEdit.setText(QtCore.QCoreApplication.translate("Dialog", self.lineEdit.text()+str(n)))
    
    def backspacePin(self):
        if len(self.lineEdit.text()):
            self.lineEdit.setText(self.lineEdit.text()[:-1])
            
    def clearPin(self):
        self.lineEdit.setText("");

    def handleLogin(self):
        if (self.lineEdit.text() == '123'):
            self.accept()
            print("Password Accepted")
        else:
            print("Password not accepted")
            wm.globalMsgWindow.showMsg(duration=4,title="Error",text="Wrong password, try again or click 'Forgot Password' to reset it")
#             qt_helper.makeMsgBox("Error",'Wrong password. Try again or click Forgot password to reset it.',icon=QtWidgets.QMessageBox.Warning)
        
        self.clearPin()
#             QtWidgets.QMessageBox.warning(
#                 self, 'Error', 'Wrong password. Try again or click Forgot password to reset it.')
            
    def registration(self):
        print("Registration")
    

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

# def handleVisibleChanged():
#     if not QtGui.QGuiApplication.inputMethod().isVisible():
#         return
#     for w in QtGui.QGuiApplication.allWindows():
#         if w.metaObject().className() == "QtVirtualKeyboard::InputView":
#             keyboard = w.findChild(QtCore.QObject, "keyboard")
#             if keyboard is not None:
#                 r = w.geometry()
#                 r.moveTop(keyboard.property("y"))
#                 w.setMask(QtGui.QRegion(r))
#                 return
if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)

    wm.globalMsgWindow = wm.MsgWindow()
    
    login = Login()
    login.setObjectName("loga")
    login.resize(800, 480)
    login.showFullScreen()
    
#     QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = Window()
        window.showFullScreen()
        sys.exit(app.exec_())

