import sys
import serial
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

#from_class = uic.loadUiType("Han_ws/PyQt/card_machine.ui")[0]


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(320, 240)
        self.linecharge = QtWidgets.QLineEdit(Dialog)
        self.linecharge.setGeometry(QtCore.QRect(120, 50, 181, 25))
        self.linecharge.setObjectName("linecharge")
        self.linepayment = QtWidgets.QLineEdit(Dialog)
        self.linepayment.setGeometry(QtCore.QRect(120, 90, 181, 25))
        self.linepayment.setObjectName("linepayment")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 50, 67, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 90, 67, 17))
        self.label_2.setObjectName("label_2")
        self.btnreset = QtWidgets.QPushButton(Dialog)
        self.btnreset.setGeometry(QtCore.QRect(200, 160, 89, 25))
        self.btnreset.setObjectName("btnreset")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "charge"))
        self.label_2.setText(_translate("Dialog", "payment"))
        self.btnreset.setText(_translate("Dialog", "reset"))

class Receiver(QThread) :
    detected = pyqtSignal(bytes)
    recvTotal = pyqtSignal(int)
    changedTotal = pyqtSignal()
    noCard = pyqtSignal()

    def __init__ (self, conn, parent=None) :
        super (Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn
        print("recv init")

    def run (self) :
        print("recv start")
        self.is_running = True
        while (self.is_running == True) :
            if self.conn.readable() :
                res = self.conn.read_until(b'\n')
                if len(res) > 0 :
                    res = res[:-2]
                    cmd = res[:2].decode()
                    print("recv total")
                    print(len(res))
                    self.recvTotal.emit(res[3:].decode())

    def stop (self) :
        print("recv stop")
        self.is_running = False

class WindowClass(QMainWindow, Ui_Dialog) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.uid = bytes(4)
        self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)

        self.recv = Receiver(self.conn)
        self.recv.start()

        self.recv.detected.connect(self.detected)
        self.recv.recvTotal.connect(self.recvTotal)

        self.timer = QTimer()
        self.timer.setInterval(3000)
        self.timer.start()

    def send (self, command, data = 0) :
        print ("send")
        req_data = struct.pack('<4s16sc', self.uid, data.encode(), b'\n')
        self.conn.write(req_data)
        return
    
    def detected(self, uid) :
        print("detected")
        self.uid = uid
        self.timer.stop()
        self.getTotal()
        self.btnreset.setDisabled(False)
        return
    
    def recvTotal(self, total) :
        print("recvTotal")
        self.linecharge.setText("")
        self.linepayment.setText("")
    
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
