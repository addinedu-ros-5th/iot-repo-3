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
                line = self.conn.read_until(b'\n')
                if (len(line)) > 0 :
                    line = line[:-2].decode()
                    print(line)
                    
    def stop (self) :
        print("recv stop")
        self.is_running = False

class WindowClass(QMainWindow, Ui_Dialog) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.conn = serial.Serial(port='COM3', baudrate=9600, timeout=1)

        self.recv = Receiver(self.conn)
        self.recv.start()
        
        self.btnread.clicked.connect(self.read)
        self.btnwrite.clicked.connect(self.write)

        self.recv.run()

    def read (self) :
        print("read")
        data = 'read'
        req_data = struct.pack('<7sc',data.encode(),b'\n')
        self.conn.write(req_data)

    def write (self) :
        print("write")
        data = 'write'
        req_data = struct.pack('<7sc',data.encode(),b'\n')
        self.conn.write(req_data)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
