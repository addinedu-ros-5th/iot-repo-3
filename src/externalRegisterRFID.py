import sys
import time
import serial
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
import mysql.connector

from_class = uic.loadUiType("./gui/invoice.ui")[0]

class Receiver(QThread) :
    def __init__ (self, conn, parent=None) :
        super (Receiver, self).__init__(parent)
        self.is_running = False
        self.is_reading = False
        self.conn = conn
        self.variableInitialize()
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
                        self.serialCommunicationState = 'Success'
                        self.is_reading = False


    def stop (self) :
        print("recv stop")
        self.is_running = False

    def variableInitialize(self) :
        self.productName = ''
        self.senderName = ''
        self.senderNumber = None
        self.senderAddress = ''
        self.serialCommunicationState = ''

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.start()
        self.DBconnect()
        self.getTestDB()
        
        self.btnRead.clicked.connect(self.invoice_Read)
        self.btnWrite.clicked.connect(self.invoice_Write)
        self.btnUpload.clicked.connect(self.setTestDB)
        self.btnDownload.clicked.connect(self.getTestDB)
        self.greet_message = struct.pack('<c', b'\n')

    def DBconnect(self):
        self.DBConn = mysql.connector.Connect(
            host = 'database-1.c96mmei8egml.ap-northeast-2.rds.amazonaws.com', 
            port = '3306',
            user = 'iot_hyc',
            password = '1',
            database = 'iot_project'
            )
        self.DBCursor = self.DBConn.cursor()

    def getTestDB(self):
        DBquery = 'SELECT * FROM order_List;'
        self.DBCursor.execute(DBquery)
        result = self.DBCursor.fetchall()
        self.list = []
        for data in result:
            self.list.append(data)
        self.row = 1
        self.recv.productName = self.list[self.row][3]
        self.recv.senderName = self.list[self.row][2]
        self.recv.senderNumber = self.list[self.row][5]
        self.recv.senderAddress = self.list[self.row][6]
        self.setMessageBox()

    def setTestDB(self):
        self.write_text()
        self.DBquery = "INSERT INTO order_List (주문자명, 제품명, 가격, 배송지) VALUES (%s, %s, %s, %s);"
        self.DBCursor.execute(self.DBquery,
                              (self.recv.senderName,
                              self.recv.productName,
                              self.recv.senderNumber,
                              self.recv.senderAddress))
        self.DBConn.commit()
        self.recv.variableInitialize()
        self.setMessageBox()

    def invoice_Read (self) :
        self.count = 0
        self.recv.variableInitialize()
        self.recv.serialCommunicationState = 'reading...'
        self.labelState.setText(self.recv.serialCommunicationState)
        req_data = struct.pack('<2sc',b'Re',b'\n')
        self.conn.write(req_data)
        self.errorTimeOut()
        self.labelState.setText(self.recv.serialCommunicationState)
        self.setMessageBox()
        print(self.count)

    def errorTimeOut(self) :
        self.recv.is_reading = True
        while (self.recv.is_reading == True) :
            self.count += 1
            if (self.count > 3000000) : 
                self.recv.serialCommunicationState = 'error : timeout'
                self.labelState.setText(self.recv.serialCommunicationState)
                break

    def invoice_Write (self) :
        self.recv.serialCommunicationState = 'writing...'
        self.labelState.setText(self.recv.serialCommunicationState)
        self.write_text()
        req_data = struct.pack('<2s4s4sH4sc',
                               b'Iw',
                               self.recv.productName.encode(),
                               self.recv.senderName.encode(),
                               int(self.recv.senderNumber),
                               self.recv.senderAddress.encode(),b'\n')
        self.conn.write(req_data)
        self.recv.variableInitialize()
        self.setMessageBox()

    def write_text(self) :
        self.recv.productName = self.lineProductName.text()
        self.recv.senderName = self.lineSenderName.text()
        self.recv.senderNumber = self.lineSenderNumber.text()
        self.recv.senderAddress = self.lineSenderAddress.text()

    def setMessageBox(self) :
        self.lineProductName.setText(self.recv.productName)
        self.lineSenderName.setText(self.recv.senderName)
        if self.recv.senderNumber != None : self.lineSenderNumber.setText(str(self.recv.senderNumber))
        else : self.lineSenderNumber.setText('')
        self.lineSenderAddress.setText(self.recv.senderAddress)



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())