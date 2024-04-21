import sys
import serial
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
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
                    print(line)

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.conn = serial.Serial(port='COM5', baudrate=9600, timeout=1)

        self.btnread.clicked.connect(self.read)
        self.btnwrite.clicked.connect(self.write)

        self.recv = Receiver(self.conn)
        self.recv.start()

    def read (self) :
        print("py : read")
        data = 'Ir'
        req_data = struct.pack('<7sc',data.encode(),b'\n')
        self.conn.write(req_data)

    def write (self) :
        print("py : write")
        data = 'Iw'
        req_data = struct.pack('<7sc',data.encode(),b'\n')
        self.conn.write(req_data)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())