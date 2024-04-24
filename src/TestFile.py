import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import mysql.connector
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import numpy as np
from PyQt5.QtCore import QTimer

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form_main = resource_path('../gui/window.ui')
form_main_class = uic.loadUiType(form_main)[0]

form_inventor = resource_path('../gui/inventor.ui')
form_inventor_class = uic.loadUiType(form_inventor)[0]

form_order = resource_path('../gui/order.ui')
form_order_class = uic.loadUiType(form_order)[0]

form_monitor = resource_path('../gui/monitor.ui')
form_monitor_class = uic.loadUiType(form_monitor)[0]

form_signin = resource_path('../gui/signin.ui')
form_signin_class = uic.loadUiType(form_signin)[0]


class WindowClass(QMainWindow, form_main_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move(100, 100)
        self.user = None
        # self.database_updater = DatabaseUpdater()

        self.inventorButton.clicked.connect(self.btn_main_to_inventor)
        self.orderButton.clicked.connect(self.btn_main_to_order)
        self.monitorButton.clicked.connect(self.btn_main_to_monitor)
        self.signinButton.clicked.connect(self.btn_main_to_signin)
        self.logoutButton.clicked.connect(self.log_out)

        self.groupBox.hide()
        self.userEdit.setReadOnly(True)


        # self.time_label = QLabel(self)
        # self.time_label.move(20, 20)  # 레이블의 위치 설정

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)



    def log_out(self):
        self.user = None
        self.groupBox.hide()
        self.groupBox_2.show()
        self.userEdit.clear()
        try:
            if self.DBConnection is not None:
                self.DBConnection.close()
                print("데이터베이스 연결이 닫혔습니다.")
        except:
            print('z')

    def btn_main_to_inventor(self):
        self.hide()
        self.inventor = InventorWindow()
        self.inventor.exec_()
        self.show()

    def btn_main_to_inventor(self):
        try:
            if self.user is not None:
                self.hide()
                self.inventor = InventorWindow()
                self.inventor.exec_()
                self.show()
            else:
                QMessageBox.warning(self, "Login required", "관리자외 출입금지", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"관리자외 출입금지", QMessageBox.Ok)


    # def btn_main_to_order(self):
    #     self.hide()
    #     self.order = OrderWindow(self.DBConnection)
    #     self.order.exec_()
    #     self.show()

    def btn_main_to_order(self):
        try:
            if self.user is not None:
                if self.DBConnection is not None:
                    self.hide()
                    self.order = OrderWindow(self.DBConnection)
                    self.order.exec_()
                    self.show()
                else:
                    QMessageBox.warning(self, "Database connection required", "관리자외 출입금지", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Login required", "관리자외 출입금지", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"관리자외 출입금지", QMessageBox.Ok)


    def btn_main_to_monitor(self):
        self.hide()
        self.monitor = MonitorWindow()
        self.monitor.exec_()
        self.show()

    def btn_main_to_signin(self):
        self.hide()
        self.signin_window = signinWindow()
        self.signin_window.login_successful.connect(self.update_user)
        self.signin_window.exec_()
        self.show()

    def update_user(self, username):

        if username:
            self.user = username
            self.userEdit.setText(username)
            self.groupBox_2.hide()
            self.groupBox.show()

        if username in self.user :  
            try:
                self.DBConnection = mysql.connector.connect(
                    host = 'database-1.c96mmei8egml.ap-northeast-2.rds.amazonaws.com', 
                    port = 3306,
                    user = 'iot_hyc',
                    password = '1',
                    database = 'iot_project'
                )
                print("데이터베이스에 연결되었습니다.")
                # self.database_updater = DatabaseUpdater()
                # self.database_thread = DatabaseThread(self.database_updater)
                # self.database_thread.start()

            except mysql.connector.Error as err:
                print("데이터베이스 연결 오류:", err)
        else:
            print("데이터베이스에 연결하지 않습니다.")

    def update_time(self):
        current_time = QDateTime.currentDateTime()
        formatted_time = current_time.toString('hh:mm:ss')
        self.timelabel.setText(formatted_time)
# -----------------------------------------------------------------------------------------

class InventorWindow(QDialog, form_inventor_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move(100, 100)
        self.mainButton.clicked.connect(self.btn_inventor_to_main)

        self.groupBox.hide()
        self.groupBox_2.hide()
        self.groupBox_3.hide()

        self.restockButton.clicked.connect(self.show_group1)
        self.placeOrderButton.clicked.connect(self.show_group2)
        self.searchButton.clicked.connect(self.show_group3)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def btn_inventor_to_main(self):
        self.close()  # 새 창 닫음

    def show_group1(self):
        self.groupBox.show()
        self.groupBox_2.hide()
        self.groupBox_3.hide()

    def show_group2(self):
        self.groupBox.hide()
        self.groupBox_2.show()
        self.groupBox_3.hide()

    def show_group3(self):
        self.groupBox.hide()
        self.groupBox_2.hide()
        self.groupBox_3.show()

#--------------------------------------------------------------------------
# class DatabaseUpdater(QObject):
#     database_updated = pyqtSignal()

#     def __init__(self):
#         super().__init__()

#     def update_database(self):
#         print("Database updated")
#         self.database_updated.emit()

# class DatabaseThread(QThread):
#     def __init__(self, database_updater):
#         super().__init__()
#         self.database_updater = database_updater

#     def run(self):
#         # 별도의 스레드에서 실행되는 메서드
#         # 데이터베이스 업데이터를 시작합니다.
#         self.database_updater.update_database()
# ---------------------------------------------------------------------------------
class OrderWindow(QDialog, form_order_class):
    def __init__(self, DBConnection):
        super().__init__()
        self.setupUi(self)
        self.move(100, 100)
        self.mainButton_o.clicked.connect(self.btn_order_to_main)
        self.btn_modify.clicked.connect(self.edit_order)
        self.btn_cancle.clicked.connect(self.cancel_order)
        # self.btn_refresh.clicked.connect(self.refresh_order)

        self.DBConnection = DBConnection
        self.load_order_list()
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_database)
        # self.timer.start(10000)

        # database_updater.database_updated.connect(self.load_order_list)

    def btn_order_to_main(self):
        self.close()

    def load_order_list(self):
        if self.DBConnection is not None:
            cursor = self.DBConnection.cursor()
            cursor.execute("SELECT * FROM order_List")
            orders = cursor.fetchall()
            cursor.close()

            self.widgetOrder.setRowCount(len(orders))
            self.widgetOrder.setColumnCount(len(orders[0]))

            for i, order in enumerate(orders):
                for j, item in enumerate(order):
                    self.widgetOrder.setItem(i, j, QTableWidgetItem(str(item)))
        else:
            print("데이터베이스에 연결되지 않았습니다.")

    def edit_order(self):
        selected_row = self.widgetOrder.currentRow()
        if selected_row >= 0:
            delivery_status_item = self.widgetOrder.item(selected_row, 10)
            if delivery_status_item is not None:
                current_status = delivery_status_item.text()

                if current_status == "준비중":
                    new_status = "배송중"
                elif current_status == "배송중":
                    new_status = "배송완료"
                else:
                    new_status = "준비중"

                delivery_status_item.setText(new_status)

                if self.DBConnection is not None:
                    cursor = self.DBConnection.cursor()
                    order_id = self.widgetOrder.item(selected_row, 0).text()
                    query = "UPDATE order_List SET 배송상태 = %s WHERE id = %s"
                    cursor.execute(query, (new_status, order_id))
                    self.DBConnection.commit()
                    cursor.close()
                    print("주문이 수정되었습니다.")
                else:
                    print("데이터베이스에 연결되지 않았습니다.")
            else:
                print("배송 상태를 수정할 수 없습니다.")
        else:
            print("수정할 주문을 선택해주세요.")

    # def cancel_order(self):
    #     selected_row = self.widgetOrder.currentRow()
    #     if selected_row >= 0:
    #         reply = QMessageBox.question(self, '주문 삭제', '선택한 주문을 취소하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #         if reply == QMessageBox.Yes:
    #             self.widgetOrder.removeRow(selected_row)

    #             if self.DBConnection is not None:
    #                 cursor = self.DBConnection.cursor()
    #                 order_id = self.widgetOrder.item(selected_row, 0).text()  # 예시: 주문 ID 가져오기
    #                 query = "DELETE FROM order_List WHERE id = %s"
    #                 cursor.execute(query, (order_id,))
    #                 self.DBConnection.commit()
    #                 cursor.close()
    #                 QMessageBox.information(self, "취소 완료", "블랙 리스트 등록완료!", QMessageBox.Ok)
    #                 print("주문이 취소되었습니다.")
    #             else:
    #                 print("데이터베이스에 연결되지 않았습니다.")
    #     else:
    #         print("취소할 주문을 선택해주세요.")

    def cancel_order(self):
        # Get the selected row
        selected_row = self.widgetOrder.currentRow()

        if selected_row >= 0:
            reply = QMessageBox.question(self, '주문 취소', '선택한 주문을 취소하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    order_id_item = self.widgetOrder.item(selected_row, 0)
                    order_id = order_id_item.text()

                    self.widgetOrder.removeRow(selected_row)

                    if self.DBConnection is not None:
                        cursor = self.DBConnection.cursor()
                        query = "DELETE FROM order_List WHERE id = %s"
                        cursor.execute(query, (order_id,))
                        self.DBConnection.commit()
                        cursor.close()
                        QMessageBox.information(self, "취소 완료", "주문이 취소되었습니다.", QMessageBox.Ok)
                        print("주문이 취소되었습니다.")
                    else:
                        QMessageBox.warning(self, "데이터베이스 연결 오류", "데이터베이스에 연결되지 않았습니다.", QMessageBox.Ok)

                except AttributeError:
                    QMessageBox.warning(self, "주문 취소 불가", "선택된 주문에 대한 주문 ID가 없습니다.", QMessageBox.Ok)

            else:
                print("취소하지 않음")

        else:
            QMessageBox.warning(self, "주문 선택 필요", "취소할 주문을 선택해주세요.", QMessageBox.Ok)


    # def refresh_order(self):
    #     self.load_order_list()
    #     print("새로고침")

    # def update_database(self):
    #     self.load_order_list()
    #     print("자동새로고침")

# -------------------------------------------------------------------------------------

class signinWindow(QDialog, form_signin_class):

    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move(100, 100)
        self.mainButton_l.clicked.connect(self.btn_signin_to_main)
        self.loginButton.clicked.connect(self.sign_in)
        self.signupButton.clicked.connect(self.sign_up)  # 회원가입 버튼에 회원가입 기능 연결

        self.radioButton_1.setChecked(True)  # Default: login mode
        self.radioButton_1.toggled.connect(self.toggle_login_signup)
        self.radioButton_2.toggled.connect(self.toggle_login_signup)

        self.groupBox.show()
        self.groupBox_2.hide()

        self.users = {
            "한영철": "1",
            "박서연": "2",
            "김민경": "3",
            "곽민기": "4"
        }
        self.user = None
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.passwordEdit_2.setEchoMode(QLineEdit.Password)
        self.passwordEdit_3.setEchoMode(QLineEdit.Password)


    def btn_signin_to_main(self):
        self.close()

    def sign_in(self):
        username = self.usernameEdit.text()
        password = self.passwordEdit.text()

        if username in self.users and self.users[username] == password:
            self.user = username
            self.login_successful.emit(username)
            self.close()

        else:
            QMessageBox.warning(self, "로그인 실패", "사용자 이름 또는 비밀번호가 올바르지 않습니다.", QMessageBox.Ok)

    def sign_up(self):
        username = self.usernameEdit_2.text()
        password = self.passwordEdit_2.text()
        password_confirm = self.passwordEdit_3.text()

        if password != password_confirm:
            QMessageBox.warning(self, "비밀번호 확인", "비밀번호가 일치하지 않습니다.", QMessageBox.Ok)
            return

        if username and password:
            if username not in self.users:
                self.users[username] = password
                QMessageBox.information(self, "회원가입 완료", "회원가입이 완료되었습니다.", QMessageBox.Ok)
                self.groupBox_2.hide()
                self.groupBox.show()
                self.radioButton_1.setChecked(True)

            else:
                QMessageBox.warning(self, "회원가입 실패", "이미 존재하는 사용자 이름입니다.", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "회원가입 실패", "사용자 이름과 비밀번호를 입력하세요.", QMessageBox.Ok)

    def toggle_login_signup(self):
        if self.radioButton_1.isChecked():  # If login mode is selected
            self.groupBox.show()
            self.groupBox_2.hide()
        elif self.radioButton_2.isChecked():  # If sign up mode is selected
            self.groupBox.hide()
            self.groupBox_2.show()

# -------------------------------------------------------------------------------------

class MonitorWindow(QDialog, form_monitor_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move(100, 100)
        self.mainButton_m.clicked.connect(self.btn_monitor_to_main)
        self.monitorOnButton.clicked.connect(self.start_stream)
        self.monitorOffButton.clicked.connect(self.stop_stream)
        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)
        self.thread = None
        self.image_label.move(20, 60)

    def btn_monitor_to_main(self):
        self.close()  # 새 창 닫음

    def start_stream(self):
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def stop_stream(self):
        if self.thread is not None:
            self.thread.stop()
            self.thread.wait()  # Wait for the thread to finish before proceeding
            self.thread = None

    def update_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
