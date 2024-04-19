from ui_Customer_Gui import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QStackedWidget
import resources_rc
import mysql.connector



#from_class = uic.loadUiType("/home/psy/src/sidebar.ui") [0]

class MySideBar(QMainWindow, Ui_MainWindow):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("SideBar Menu")

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 

        self.connect_mysql()

        #self.icon_name_widget.setHidden(True)


        #카테고리 클릭 이벤트
        self.dashboard_1.clicked.connect(self.switch_to_dashboardPage)
        self.dashboard_2.clicked.connect(self.switch_to_dashboardPage)

        self.login_1.clicked.connect(self.switch_to_loginPage)
        self.login_2.clicked.connect(self.switch_to_loginPage)

        self.foodgrocery_1.clicked.connect(self.switch_to_foodgroceryPage)
        self.foodgrocery_2.clicked.connect(self.switch_to_foodgroceryPage)

        self.home_1.clicked.connect(self.switch_to_homePage)
        self.home_2.clicked.connect(self.switch_to_homePage)

        self.beautyhealth_1.clicked.connect(self.switch_to_beautyhealthPage)
        self.beautyhealth_2.clicked.connect(self.switch_to_beautyhealthPage)
        
        self.cart_1.clicked.connect(self.switch_to_cartPage)
        self.cart_2.clicked.connect(self.switch_to_cartPage)

        ## dashboard 클릭 이벤트 
        # 가격 클릭 시 해당 상품 포함된 카테고리로 이동
        self.btndashboard1.clicked.connect(self.switch_to_foodgroceryPage)
        self.btndashboard2.clicked.connect(self.switch_to_foodgroceryPage)
        self.btndashboard3.clicked.connect(self.switch_to_homePage)
        self.btndashboard4.clicked.connect(self.switch_to_homePage)
        self.btndashboard5.clicked.connect(self.switch_to_beautyhealthPage)
        self.btndashboard6.clicked.connect(self.switch_to_beautyhealthPage)
        self.btndashboard7.clicked.connect(self.switch_to_foodgroceryPage)
        self.btndashboard8.clicked.connect(self.switch_to_homePage)
        # 카트 버튼 클릭 시 장바구니 카테고리로 이동
        self.btncart.clicked.connect(self.switch_to_cartPage)

        # 각 카테고리 페이지에서 buy 버튼 클릭 시 장바구니로 이동
        self.btnbuy1.clicked.connect(self.cliked_buy_button)
        self.btnbuy2.clicked.connect(self.cliked_buy_button)
        self.btnbuy3.clicked.connect(self.get_text)

        #장바구니에서 삭제 클릭시 삭제
        #self.tableWidget.cellClicked.connect(self.deleteRowByLastCellTextClick)

        self.btnSearch.clicked.connect(self.search_item)



    def switch_to_dashboardPage(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_loginPage(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_foodgroceryPage(self):
        self.stackedWidget.setCurrentIndex(2)

    def switch_to_homePage(self):
        self.stackedWidget.setCurrentIndex(3)

    def switch_to_beautyhealthPage(self):
        self.stackedWidget.setCurrentIndex(4)

    def switch_to_cartPage(self):
        self.stackedWidget.setCurrentIndex(5)

    #카테고리에서 buy 버튼 클릭 시 상품명, 가격, 수량 장바구니로 이동
    def cliked_buy_button(self):
        text_product_name = self.productname1.text()
        text_price = self.price1.text()
        self.stackedWidget.setCurrentIndex(5)
        product_name = QTableWidgetItem(text_product_name)
        price =  QTableWidgetItem(text_price)
        self.tableWidget.setItem(0, 0, product_name)
        self.tableWidget.setItem(0, 1, QTableWidgetItem('1')) 
        self.tableWidget.setItem(0, 2, price) 

    def get_text(self):
        
        sender_button = self.sender() 
        button_name = sender_button.objectName()  
        text_product_name = sender_button.text()  
        print("Clicked button name:", text_product_name)


    
    def add_cart(self):
        row_position = len(self.data) - 1 
        self.table_widget.insertRow(row_position)
        for col, value in enumerate(new_data):
            item = QTableWidgetItem(str(value))
            self.table_widget.setItem(row_position, col, item)

    def test_clicked(self):
        sender_button = self.sender() 
        button_name = sender_button.objectName() 
        print("Clicked button name:", button_name)


    def connect_mysql(self):
        self.local = mysql.connector.connect(
            host = 'localhost',
            user = "root",
            password = "0000",
            database='PJ2' 
        )

    #검색창에서 상품명 검색
    def search_item(self):
        productName = self.searchBar.text()
        cur = self.local.cursor()
        cur.execute("SELECT * FROM Products WHERE productName = %s", (productName,))
        result = cur.fetchall()
        second_value = result[0] #list
        self.display_result(result)

        
        

        if result:
            all_labels = self.findChildren(QLabel)
            for label in all_labels:
                if label.text() == "test":
                    stacked_widget = self.findChild(QStackedWidget)
                    parent_widget = label.parentWidget()
                    index = stacked_widget.indexOf(parent_widget)
                    stacked_widget.setCurrentIndex(index)
                    #5self.foodgrocery_1.setChecked(True)

                    

    def display_result(self, result):
        self.tableWidget.setRowCount(0)
        if result:
            for row_num, row_data in enumerate(result):
                self.tableWidget.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        else:
            print("해당 제품이 없습니다.") 


        

        

