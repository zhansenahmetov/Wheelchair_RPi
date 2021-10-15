"""
This file is responsible for replacing QMessageBox, allowing more flexibility, especially with threads.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
import QT_Helpers as qt_helper
import time

globalMsgWindow = None  # global to hold universal message window


class MsgWindow(QtWidgets.QMainWindow):
    """
    This class will enable a small, temporary, window to circumvent
    issues with using QMessageBoxes from threads
    """

    def __init__(self, width=500, height=150):
        """
        This function initializes the pop-up message window

        :param width: Width of the window
        :param height: Height of the window
        """
        super().__init__()
        #         self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.width = width
        self.height = height
        self.setFixedSize(width, height)

        # Center the Message Box
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.msgLabel = QtWidgets.QLabel(self)
        self.msgLabel.setGeometry(QtCore.QRect(width * 0.1, height * 0.1, width * 0.8, height * 0.8))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.msgLabel.setFont(font)
        self.msgLabel.setObjectName("label_15")
        self.msgLabel.setText("text")
        self.msgLabel.setWordWrap(True)
        self.msgLabel.setAlignment(QtCore.Qt.AlignCenter)

    def showMsg(self, title='Title', text='text', color='yellow', duration=2, callback=[None, None]):
        """
        This function can be called to show the pop-up window to display a message

        :param title: Title of the pop-up window
        :param text: Message content of the pop-up window
        :param color: Background color of the pop-up window (in CSS format: 'background-color: <color>')
        :param duration: Pop-up window duration in seconds
        :param callback: Function to call at the end of pop-up duration [function,parameter]
        """
        self.setWindowTitle(title)
        self.msgLabel.setText(text)
        self.setStyleSheet("background-color: " + str(color))
        self.show()
        if duration:
            try:
                if callback[0]:
                    qt_helper.DelayAction(duration, [self.hide, None], [callback[0], callback[1]]).start()
                else:
                    qt_helper.DelayAction(duration, [self.hide, None]).start()
            except Exception as e:
                print("Encountered Error: ", e)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow2 = MsgWindow()
    MainWindow2.showMsg(text="This is a test message.", title="Warning")
    sys.exit(app.exec_())
