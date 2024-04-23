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
    def __init__ (self, arduinoConnection, parent=None) :
        super (Receiver, self).__init__(parent)
        self.is_running = False
        self.is_reading = False
        self.arduinoConnection = arduinoConnection
        self.variableInitialize()
        print("recv init")

    def run (self) :
        print("recv start")
        self.is_running = True
        while (self.is_running == True) :
            if self.arduinoConnection.readable() :
                line = self.arduinoConnection.read_until(b'\n')
                if (len(line)) > 0 :
                    line = line[:-2]
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

        self.arduinoConnection = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
        self.recv = Receiver(self.arduinoConnection)
        self.recv.start()
        self.connectToDB()
        self.getFromDB()
        
        self.btnRead.clicked.connect(self.orderRead)
        self.btnWrite.clicked.connect(self.orderWrite)
        self.btnUpload.clicked.connect(self.enrollment)
        self.btnDownload.clicked.connect(self.getFromDB)
        self.greet_message = struct.pack('<c', b'\n')

    def connectToDB(self):
        self.DBConnection = mysql.connector.Connect(
            host = 'database-1.c96mmei8egml.ap-northeast-2.rds.amazonaws.com', 
            port = '3306',
            user = 'iot_hyc',
            password = '1',
            database = 'iot_project'
            )
        self.DBCursor = self.DBConnection.cursor()

    def getFromDB(self):
        DBquery = 'SELECT * FROM order_List;'
        self.DBCursor.execute(DBquery)
        result = self.DBCursor.fetchall()
        self.list = []
        for data in result:
            self.list.append(data)
        self.row = 0
        self.recv.productName = self.list[self.row][3]
        self.recv.senderName = self.list[self.row][2]
        self.recv.senderNumber = self.list[self.row][5]
        self.recv.senderAddress = self.list[self.row][6]
        self.setTextToGUI()

    def enrollment(self):
        self.getTextfromGUI()
        self.DBquery = "INSERT INTO order_List (주문자명, 제품명, 가격, 배송지) VALUES (%s, %s, %s, %s);"
        self.DBCursor.execute(self.DBquery,
                              (self.recv.senderName,
                              self.recv.productName,
                              self.recv.senderNumber,
                              self.recv.senderAddress))
        self.DBConnection.commit()
        self.recv.variableInitialize()
        self.setTextToGUI()

    def orderRead (self) :
        self.count = 0
        self.recv.variableInitialize()
        self.recv.serialCommunicationState = 'reading...'
        self.labelState.setText(self.recv.serialCommunicationState)
        req_data = struct.pack('<2sc',b'Re',b'\n')
        self.arduinoConnection.write(req_data)
        self.errorTimeOut()
        self.labelState.setText(self.recv.serialCommunicationState)
        self.setTextToGUI()
        print(self.count)

    def errorTimeOut(self) :
        self.recv.is_reading = True
        while (self.recv.is_reading == True) :
            self.count += 1
            if (self.count > 3000000) : 
                self.recv.serialCommunicationState = 'error : timeout'
                self.labelState.setText(self.recv.serialCommunicationState)
                break

    def orderWrite (self) :
        self.recv.serialCommunicationState = 'writing...'
        self.labelState.setText(self.recv.serialCommunicationState)
        self.getTextfromGUI()
        req_data = struct.pack('<2s4s4sH4sc',
                               b'Iw',
                               self.recv.productName.encode(),
                               self.recv.senderName.encode(),
                               int(self.recv.senderNumber),
                               self.recv.senderAddress.encode(),b'\n')
        self.arduinoConnection.write(req_data)
        self.recv.variableInitialize()
        self.setTextToGUI()
        self.recv.serialCommunicationState = 'Success'
        self.labelState.setText(self.recv.serialCommunicationState)

    def getTextfromGUI(self) :
        self.recv.productName = self.lineProductName.text()
        self.recv.senderName = self.lineSenderName.text()
        self.recv.senderNumber = self.lineSenderNumber.text()
        self.recv.senderAddress = self.lineSenderAddress.text()

    def setTextToGUI(self) :
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