import sys
import time
import serial
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from_class = uic.loadUiType("./gui/invoice.ui")[0]

class Receiver(QThread) :
    def __init__ (self, conn, parent=None) :
        super (Receiver, self).__init__(parent)
        self.is_running = False
        self.is_reading = False
        self.conn = conn
        self.productName = ''
        self.senderName = ''
        self.senderNumber = 0
        self.senderAddress = ''
        print("recv init")

    def run (self) :
        print("recv start")
        self.is_running = True
        while (self.is_running == True) :
            if self.conn.readable() :
                line = self.conn.read_until(b'\n')
                if (len(line)) > 0 :
                    line = line[:-2]
                    if line[:2].decode() == "HI" :
                        self.productName = line[2:].decode()
                    if line[:2].decode() == "Ir" :
                        self.productName = line[2:6].decode()
                        self.senderName = line[6:10].decode()
                        self.senderNumber = int.from_bytes(line[10:12], 'little')
                        self.senderAddress = line[12:16].decode()
                        self.is_reading = False

                

    def stop (self) :
        print("recv stop")
        self.is_running = False

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.start()
        
        self.btnRead.clicked.connect(self.invoice_Read)
        self.btnEnter.clicked.connect(self.invoice_Write)
        self.greet_message = struct.pack('<c', b'\n')

    def invoice_Read (self) :
        self.count = 0
        print("read")
        req_data = struct.pack('<2sc',b'Re',b'\n')
        self.conn.write(req_data)
        self.recv.is_reading = True
        while (self.recv.is_reading == True) :
            self.count += 1
            if (self.count > 3000000) : break
        self.lineProductName.setText(self.recv.productName)
        self.lineSenderName.setText(self.recv.senderName)
        self.lineSenderNumber.setText(str(self.recv.senderNumber))
        self.lineSenderAddress.setText(self.recv.senderAddress)
        print(self.count)
        print(self.recv.productName)


    def invoice_Write (self) :
        print("write")
        self.write_text()
        req_data = struct.pack('<2s4s4sH4sc',
                               b'Iw',
                               self.enterProductName.encode(),
                               self.enterSenderName.encode(),
                               int(self.enterSenderNumber),
                               self.enterSenderAddress.encode(),b'\n')
        self.conn.write(req_data)

    def write_text(self) :
        self.cmd = 'Iw'
        self.enterProductName = self.lineProductName.text()
        self.enterSenderName = self.lineSenderName.text()
        self.enterSenderNumber = self.lineSenderNumber.text()
        self.enterSenderAddress = self.lineSenderAddress.text()


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
