import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QStackedWidget
import resources_rc
import mysql.connector
import re
import datetime


from_class = uic.loadUiType("./main/gui/Customer_Gui.ui") [0]


class WindowClass(QMainWindow, from_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("SideBar Menu")

        self.Customer_Gui_tablewidgetCartList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        

        self.connect_mysql()

        self.start_stock_label()
        
        self.click_count = 0 #아이디 중복확인 여부 확인용
        self.login_count = 0 #로그인 여부 확인용
    

        #카테고리 클릭 시 해당 페이지 로드
        self.Customer_Gui_btnHomePage_1.clicked.connect(self.switch_to_dashboardPage)
        self.Customer_Gui_btnHomePage_2.clicked.connect(self.switch_to_dashboardPage)
        self.Customer_Gui_btnLoginPage_1.clicked.connect(self.switch_to_loginPage)
        self.Customer_Gui_btnLoginPage_2.clicked.connect(self.switch_to_loginPage)
        self.Customer_Gui_btnFoodandGroceryPage_1.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnFoodandGroceryPage_2.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnSportsandOutdoorsPage_1.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnSportsandOutdoorsPage_2.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnBeautyandHealthPage_1.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnBeautyandHealthPage_2.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnTrackPackagePage_1.clicked.connect(self.switch_to_trackpackagePage)
        self.Customer_Gui_btnTrackPackagePage_2.clicked.connect(self.switch_to_trackpackagePage)

        # 홈페이지에서 가격 클릭 시 해당 상품 포함된 페이지 로드
        self.Customer_Gui_btnConnCategory_1.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_2.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_3.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnConnCategory_4.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnConnCategory_5.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnConnCategory_6.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnConnCategory_7.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_8.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnConnCategory_9.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_10.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_11.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnConnCategory_12.clicked.connect(self.switch_to_sportsoutdoorsPage)
        self.Customer_Gui_btnConnCategory_13.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnConnCategory_14.clicked.connect(self.switch_to_beautyhealthPage)
        self.Customer_Gui_btnConnCategory_15.clicked.connect(self.switch_to_foodgroceryPage)
        self.Customer_Gui_btnConnCategory_16.clicked.connect(self.switch_to_sportsoutdoorsPage)


        # 카트 버튼 클릭 시 장바구니 페이지 로드
        self.Customer_Gui_btnCart.clicked.connect(self.switch_to_cartPage)

        # Add cart 버튼 클릭 시 장바구니에 추가
        self.Customer_Gui_btnAddCart_1.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_2.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_3.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_4.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_5.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_6.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_7.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_8.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_9.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_10.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_11.clicked.connect(self.clicked_add_cart_btn)
        self.Customer_Gui_btnAddCart_12.clicked.connect(self.clicked_add_cart_btn)

        #검색창에서 상품검색
        self.Customer_Gui_btnSearch.clicked.connect(self.search_product)
        self.Customer_Gui_lineSearchBar.returnPressed.connect(self.search_product)

        #header 클릭 시 홈페이지 로드
        self.Customer_Gui_btnHeader.clicked.connect(self.switch_to_dashboardPage)

        #장바구니에서 구매하기 클릭
        self.Customer_Gui_btnCartPageBuy.clicked.connect(self.sign_up)
        self.Customer_Gui_btnLoginPageSignUp.clicked.connect(self.switch_to_signupPage)

        #장바구니에서 삭제하기 클릭
        self.Customer_Gui_btnDelete.clicked.connect(self.delete_cart)

        #회원가입 버튼 클릭
        self.Customer_Gui_lineSignUpPageSignUp.clicked.connect(self.clicked_sign_up_btn)

        #아이디 중복확인 버튼 클릭
        self.Customer_Gui_btnCheckID.clicked.connect(self.clicked_checked_ID_btn)

        #로그인 버튼 클릭
        self.Customer_Gui_btnLogin.clicked.connect(self.switch_to_loginPage)
        self.Customer_Gui_btnLoginPageLogin.clicked.connect(self.clicked_login_btn)

        # 결제하기 버튼 클릭
        self.Customer_Gui_btnOrderPageBuy.clicked.connect(self.clicked_orderPage_btnbuy)
        self.Customer_Gui_btnCheck.clicked.connect(self.clicked_check_delivery_btn)



    def switch_to_dashboardPage(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_loginPage(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_foodgroceryPage(self):
        self.stackedWidget.setCurrentIndex(2)

    def switch_to_sportsoutdoorsPage(self):
        self.stackedWidget.setCurrentIndex(3)

    def switch_to_beautyhealthPage(self):
        self.stackedWidget.setCurrentIndex(4)

    def switch_to_cartPage(self):
        self.stackedWidget.setCurrentIndex(5)

    def switch_to_signupPage(self):
        self.stackedWidget.setCurrentIndex(6)

    def switch_to_trackpackagePage(self):
        self.stackedWidget.setCurrentIndex(8)

    #카테고리에서 buy 버튼 클릭 시 상품명, 가격, 수량 장바구니로 이동
    def clicked_add_cart_btn(self):

        #클릭된 btnBuynum와 같은 QFrame 있는 가격(labelnum), 수량(spinboxnum) 의 num은 동일
        clicked_btnAddCart = self.sender()
        btnAddcart = clicked_btnAddCart.objectName()
        print(btnAddcart)
        num = re.findall(r'\d+', btnAddcart)
        self.text_product_name = getattr(self, f"Customer_Gui_labelProductName_{num[0]}").text()
        self.text_Quantity = getattr(self, f"Customer_Gui_spinboxQuantity_{num[0]}").value()
        self.text_price = getattr(self, f"Customer_Gui_labelPrice_{num[0]}").text()
        self.total_price = int(self.text_Quantity) * int(self.text_price)

        self.product_name = QTableWidgetItem(self.text_product_name)
        self.Quantity =  QTableWidgetItem(str(self.text_Quantity))
        self.price =  QTableWidgetItem(str(self.total_price))

        self.add_cart()
        QMessageBox.information(self, "Information", "상품이 장바구니에 담겼습니다.")
        #수량 1값으로
        reset_quantity = 1
        getattr(self, f"Customer_Gui_spinboxQuantity_{num[0]}").setValue(reset_quantity)
        
        #stocks_list 보유수량 stock label에 명시
        cur = self.remote.cursor()
        cur.execute("SELECT stock FROM stocks_list WHERE productName = %s", (self.text_product_name,))
        self.present_stock = cur.fetchone()
        print(self.present_stock)
        getattr(self, f"Customer_Gui_labelStock_{num[0]}").setText(str(self.present_stock[0]))


    def add_cart(self):
        
        new_product_name = self.product_name.text()

        existing_row = -1
        for row in range(self.Customer_Gui_tablewidgetCartList.rowCount()):
            item = self.Customer_Gui_tablewidgetCartList.item(row, 0)
            if item and item.text() == new_product_name:
                existing_row = row
                break

        if existing_row != -1:
            current_quantity = int(self.Customer_Gui_tablewidgetCartList.item(existing_row, 1).text())
            new_quantity = current_quantity + self.text_Quantity
            self.Customer_Gui_tablewidgetCartList.setItem(existing_row, 1, QTableWidgetItem(str(new_quantity)))
        else:
            current_row_count = self.Customer_Gui_tablewidgetCartList.rowCount() 
            self.Customer_Gui_tablewidgetCartList.insertRow(current_row_count)
            self.Customer_Gui_tablewidgetCartList.setCellWidget(current_row_count, 3, QCheckBox())
            self.Customer_Gui_tablewidgetCartList.setItem(current_row_count, 0, self.product_name)
            self.Customer_Gui_tablewidgetCartList.setItem(current_row_count, 1, QTableWidgetItem(str(self.text_Quantity))) 
            self.Customer_Gui_tablewidgetCartList.setItem(current_row_count, 2, self.price)

        # stacks_lists 보유수량 수정
        cur = self.remote.cursor()
        cur.execute("UPDATE stocks_list SET stock = stock - %s WHERE productName = %s", (int(self.text_Quantity), self.text_product_name))
        self.remote.commit()

        

    def start_stock_label(self):
        cur = self.remote.cursor()
        cur.execute("SELECT stock FROM stocks_list WHERE productName = '사과'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_1.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '청포도'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_2.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '오레오'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_3.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '코카콜라'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_4.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '야구공'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_5.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '농구공'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_6.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '볼링공'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_7.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '운동화'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_8.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '립스틱'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_9.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '크림'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_10.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '비타민'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_11.setText(str(start_stock[0]))

        cur.execute("SELECT stock FROM stocks_list WHERE productName = '덤벨'")
        start_stock = cur.fetchone()
        self.Customer_Gui_labelStock_12.setText(str(start_stock[0]))
        
    

    def delete_cart(self):
 
        # 체크된 체크박스가 있는 행 확인
        for row in range(self.Customer_Gui_tablewidgetCartList.rowCount()):
            check_box_item = self.Customer_Gui_tablewidgetCartList.cellWidget(row, 3)
            if isinstance(check_box_item, QCheckBox) and check_box_item.isChecked():
        
                # storage_table에서 보유수량 원복
                delete_product = self.Customer_Gui_tablewidgetCartList.item(row, 0).text()
                quantity_text = int(self.Customer_Gui_tablewidgetCartList.item(row, 1).text())
                cur = self.remote.cursor()
                cur.execute("UPDATE stocks_list SET stock = stock + %s WHERE productName = %s", (quantity_text, delete_product))
                self.remote.commit()
                self.Customer_Gui_tablewidgetCartList.removeRow(row)

                #storage_table에서 보유수량 변경된 만큼 stock lable에 명시
                cur = self.remote.cursor()
                cur.execute("SELECT stock FROM stocks_list WHERE productName  = %s", (delete_product,))
                self.present_stock = cur.fetchone()
                print(self.present_stock)
                all_labels = self.findChildren(QLabel)
                for label in all_labels:
                    if label.text() == delete_product: 
                        label_name = label.objectName()
                        print(label_name)
                        label_num = re.findall(r'\d+', label_name)
                        print(label_num)
                        getattr(self, f"Customer_Gui_labelStock_{label_num[0]}").setText(str(self.present_stock[0])) #상세페이지 내삭제물품의 남은 수량 수정
                       

            

    def sign_up(self):

        if (self.login_count == 1): # 로그인하고 구매하기 버튼 누르면 주문결제 페이지 로드
            if (self.Customer_Gui_tablewidgetCartList.rowCount() == 0):
                QMessageBox.information(self, "Information", "장바구니가 비었습니다.")
            else:
                self.stackedWidget.setCurrentIndex(7)   
        elif (self.login_count == 0): # 장바구니에 아무것도 안담겨 있을 경우
            QMessageBox.information(self, "Information", "로그인이 필요합니다.")
            self.stackedWidget.setCurrentIndex(6)
            self.Customer_Gui_btnCheckID.clicked.connect(self.clicked_checked_ID_btn)



    def clicked_checked_ID_btn(self):
        ID = self.Customer_Gui_lineSignUpPageID.text() 
        cur = self.remote.cursor()
        cur.execute("SELECT * FROM users_list WHERE loginID = %s", (ID,))
        result = cur.fetchall()
        self.click_count = 1

        if result:
            QMessageBox.information(self, "Information", "사용할 수 없는 아이디입니다.")
        else:
            QMessageBox.information(self, "Information", "사용 가능한 아이디입니다.")
            self.Customer_Gui_lineSignUpPageSignUp.setEnabled(True)



    def clicked_sign_up_btn(self):

        if (self.click_count == 1) : #ID 중복 확인을 했다면
            # users_list에 ID, PW, 이름, 핸드폰 번호 추가
            self.ID = self.Customer_Gui_lineSignUpPageID.text()
            self.PW = self.Customer_Gui_lineSignUpPagePW.text()
            self.Name = self.Customer_Gui_lineSignUpPageName.text()
            self.PhoneNumber = self.Customer_Gui_lineSignUpPagePhoneNumber.text() 
            cur_u = self.remote.cursor()
            cur_u.execute("INSERT INTO users_list VALUES (%s, %s, %s, %s, %s);", (None, self.ID, self.PW, self.Name, self.PhoneNumber))
            self.remote.commit()
            self.Customer_Gui_lineSignUpPageID.clear()
            self.Customer_Gui_lineSignUpPagePW.clear()
            self.Customer_Gui_lineSignUpPageName.clear()
            self.Customer_Gui_lineSignUpPagePhoneNumber.clear()
            QMessageBox.information(self, "Information", "회원가입이 완료되었습니다.")
            self.stackedWidget.setCurrentIndex(1) #로그인 페이지 로드
            self.click_count = 0
        else :
            QMessageBox.information(self, "Information", "아이디 중복확인을 해주세요.")


    def clicked_login_btn(self):
        #로그인 상태 구분
        if (self.login_count == 1):
            QMessageBox.information(self, "Information", "로그아웃 되었습니다.")
            self.Customer_Gui_btnLogin.setText("로그인")
            self.Customer_Gui_btnLoginPageLogin.setText("로그인")
            self.Customer_Gui_lineLoginPageID.show()
            self.Customer_Gui_LoginPagePW.show()
            self.labelLoginID.show()
            self.labelLoginPW.show()
            self.login_count = 0


        else:
            self.UserID = self.Customer_Gui_lineLoginPageID.text()
            self.UserPW = self.Customer_Gui_LoginPagePW.text()
            
            if (self.UserID == "" and self.UserPW == ""):
                QMessageBox.information(self, "Information", "아이디와 비밀번호를 입력해주세요.")
            elif (self.UserPW == ""):
                QMessageBox.information(self, "Information", "비밀번호를 입력해주세요.")
            elif (self.UserID == ""):
                QMessageBox.information(self, "Information", "아이디를 입력해주세요.")
            else :
                cur_l = self.remote.cursor()
                cur_l.execute("SELECT * FROM users_list WHERE loginID = %s and loginPW = %s", (self.UserID, self.UserPW ))
                result = cur_l.fetchall()

                if result:                    
                    QMessageBox.information(self, "Information", "로그인 되었습니다.") 
                    self.Customer_Gui_lineLoginPageID.clear()
                    self.Customer_Gui_LoginPagePW.clear()
                    self.stackedWidget.setCurrentIndex(5)
                    self.login_count = 1
                    self.Customer_Gui_btnLogin.setText("로그아웃")
                    self.Customer_Gui_btnLoginPageLogin.setText("로그아웃")
                    self.Customer_Gui_lineLoginPageID.hide()
                    self.Customer_Gui_LoginPagePW.hide()
                    self.labelLoginID.hide()
                    self.labelLoginPW.hide()

                else:
                    QMessageBox.information(self, "Information", "아이디 또는 비밀번호가 틀렸습니다. 다시 확인해 주세요.")

   
    def clicked_orderPage_btnbuy(self):  
        
        self.userName = self.Customer_Gui_lineOrderPageUserName.text()
        self.userPhoneNumber = self.Customer_Gui_lineOrderPagePhoneNumber.text()
        self.orderPW = self.Customer_Gui_lineOrderPageOrderPW.text()
        self.orderAddress = self.Customer_Gui_lineOrderPageOrderAddress.text()
        
        #장바구니 tablewidget 순서대로 읽어오기 (제품명, 수량)
        for row in range(self.Customer_Gui_tablewidgetCartList.rowCount()):
            self.orderProductName = self.Customer_Gui_tablewidgetCartList.item(row, 0).text()
            self.orderQuantity = self.Customer_Gui_tablewidgetCartList.item(row, 1).text()

            cur_o = self.remote.cursor()
            cur_o.execute("""
                INSERT INTO orders_list (ID, orderPW, name, phoneNumber, address, productName, quantity, orderDate)
                SELECT ID, %s, %s, %s, %s, %s, %s, %s
                FROM users_list
                WHERE loginID = %s
            """, (self.orderPW, self.userName, self.userPhoneNumber, self.orderAddress, self.orderProductName, int(self.orderQuantity), datetime.datetime.now(), self.UserID))

            self.remote.commit()

        QMessageBox.information(self, "Information", "주문이 완료되었습니다.")
        
        self.Customer_Gui_lineOrderPageUserName.clear()
        self.Customer_Gui_lineOrderPagePhoneNumber.clear()
        self.Customer_Gui_lineOrderPageOrderPW.clear()
        self.Customer_Gui_lineOrderPageOrderAddress.clear()


    def connect_mysql(self):
        self.remote = mysql.connector.connect(
            host = 'database-1.c96mmei8egml.ap-northeast-2.rds.amazonaws.com',
            port = 3306,
            user = "iot_psy",
            password = "1",
            database='iot_project' 
        )

    #검색창에서 상품명 검색시 상품페이지로 이동
    def search_product(self):
        
        productName = self.Customer_Gui_lineSearchBar.text() #검색된 text
        print(productName)
        cur = self.remote.cursor()
        cur.execute("SELECT * FROM stocks_list WHERE productName = %s;", (productName,))
        result = cur.fetchall()
        print(result)

        if result:
            all_labels = self.findChildren(QLabel)
            for label in all_labels:
                if label.text() == productName: 
                
                    grand_parent_widget = label.parentWidget().parentWidget().parentWidget() #상품명이 text에 삽입되어 있는 label의 page widget
                    index = self.stackedWidget.indexOf(grand_parent_widget) #page widget의 index
                    self.stackedWidget.setCurrentIndex(index) #상품명있는 page 로드
        else:
            QMessageBox.information(self, "Information", "검색하신 '%s'에 대한 검색결과가 없습니다" %productName)

    def clicked_check_delivery_btn(self):
        order_ID = self.Customer_Gui_lineUserID.text()
        order_PW = self.Customer_Gui_lineOrderPW.text()
        if(order_ID == "" and order_ID == ""):
            QMessageBox.information(self, "Information", "주문 ID 및 주문 PW를 입력해주세요.")
        elif (order_ID == ""):
            QMessageBox.information(self, "Information", "주문 ID를 입력해주세요.")
        elif (order_ID == ""):
            QMessageBox.information(self, "Information", "주문 PW를 입력해주세요.")
        else:
            cur = self.remote.cursor()
            cur.execute("SELECT * FROM orders_list WHERE ID = %s and orderPW = %s;", (order_ID, order_PW))
            order_information = cur.fetchall()
            if order_information:

                cur_d = self.remote.cursor()
                cur_d.execute("SELECT ID FROM orders_list WHERE orderPW = %s;", (order_PW,))
                orders_list_row = cur_d.fetchall()
                ID = orders_list_row[1][0]
                cur_d.execute("SELECT * FROM delivery_status WHERE orderPW = %s;", (ID,))
                delivery_status_row = cur_d.fetchall()
                delivery_status_preparingDelivery = delivery_status_row[5]
                delivery_status_Arrive = delivery_status_row[6]
                delivery_status_Left = delivery_status_row[7]
                delivery_status_startDelivery = delivery_status_row[8]

                if (delivery_status_preparingDelivery == True):
                    self.Customer_Gui_lineDeliveryInfo.setText("배송준비중")
                elif (delivery_status_Arrive == True):
                    self.Customer_Gui_lineDeliveryInfo.setText("간선상차")
                elif (delivery_status_Left == True):
                    self.Customer_Gui_lineDeliveryInfo.setText("간선하차")
                elif (delivery_status_startDelivery == True):
                    self.Customer_Gui_lineDeliveryInfo.setText("배송시작")   
            else:
                QMessageBox.information(self, "Information", "배송정보가 없습니다.")
                
        
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
