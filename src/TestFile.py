import sys
import time
import serial
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from_class = uic.loadUiType("./gui/test.ui")[0]

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
                    if line[:2] == "Ir" :
                        self.id = line[2:]
                        print("Id : ", self.id)
                    elif line[:2] == "Nr" :
                        self.name = line[2:]
                        print("name : ", self.name)
                    elif line[:2] == "nr" :
                        self.num = line[2:]
                        print("num : ", self.num)
                    
    def stop (self) :
        print("recv stop")
        self.is_running = False

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.conn = serial.Serial(port='COM5', baudrate=115200, timeout=1)

        self.recv = Receiver(self.conn)
        self.recv.start()
        
        self.btnread.clicked.connect(self.read)
        self.btnwrite.clicked.connect(self.write)

    def read (self) :
        print("read")
        req_data = struct.pack('<2sc',b'Re',b'\n')
        self.conn.write(req_data)
        time.sleep(1)

    def write (self) :
        print("write")
        self.write_text()
        req_data = struct.pack('<2s8sc',b'Iw',self.write_id.encode(),b'\n')
        self.conn.write(req_data)

    def write_text(self) :
        self.write_id = self.lineEdit.text()
        print("Text in line edit:", self.write_id)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
