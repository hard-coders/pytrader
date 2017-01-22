"""
File Name   : pytrader.py
Author      : Spike Lee
Date        : 2017.01.21

Load UI and handle events
"""
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from Kiwoom import *

gui = uic.loadUiType("pytrader.ui")[0]

class MainWindow(QMainWindow, gui):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		
		self.kiwoom = Kiwoom()
		self.kiwoom.commConnect()
		
		# get user account ID/PW
		self.account = []
		with open("account.txt", 'r') as f:
			self.account = f.readlines()
		
		# get account info
		account_cnt  = int(self.kiwoom.getLoginInfo("ACCOUNT_CNT"))
		account_no   = self.kiwoom.getLoginInfo("ACCNO")
		account_list = account_no.split(';')[0:account_cnt]
		
		# timer in status bar
		self.timer_status_bar = QTimer(self)
		self.timer_status_bar.start(1000)
		self.timer_status_bar.timeout.connect(self.timeoutStatusBar)
		
		# timer in table widgets
		self.timer_table = QTimer(self)
		self.timer_table.start(10000)
		self.timer_table.timeout.connect(self.timeoutBalanceTable)
		
		# Window forms
		self.qtOrder_comboBox_account.addItems(account_list)
		self.qtOrder_lineEdit_item.textChanged.connect(self.itemCodeChanged)
		self.qtOrder_pushButton_sendOrder.clicked.connect(self.sendOrder)
		self.qtTrade_pushButton_check.clicked.connect(self.checkBalance)
		
	def timeoutStatusBar(self):
		current_time = QTime.currentTime()
		text_time = current_time.toString("hh:mm:ss")
		time_msg = "현재시간 : " + text_time
		
		if self.kiwoom.getConnectState() == 1:
			state_msg = "서버 연결 중"
		else:
			state_msg = "서버 끊김"
			
		self.statusBar = QStatusBar(self)
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage(state_msg + " | " + time_msg)
	
	def timeoutBalanceTable(self):
		if self.qtTrade_checkBox_realtime.isChecked() == True:
			self.checkBalance()
		
	def itemCodeChanged(self):
		""" print item code by hangul """
		code = self.qtOrder_lineEdit_item.text()
		name = self.kiwoom.getMasterCodeName(code)
		self.qtOrder_lineEdit_code.setText(name)
		
	def sendOrder(self):
		order_type_lookup = {"신규매수":1, "신규매도":2, "매수취소":3, "매도취소":4}
		bid_lookup        = {"지정가":"00", "시장가":"03"}

		account     = self.qtOrder_comboBox_account.currentText()
		order_type  = self.qtOrder_comboBox_order.currentText()
		code        = self.qtOrder_lineEdit_item.text()
		bid         = self.qtOrder_comboBox_type.currentText()
		num         = self.qtOrder_spinBox_qty.value()
		price       = self.qtOrder_spinBox_price.value()

		e = self.kiwoom.sendOrder("sendOrder_req", "0101", account, order_type_lookup[order_type], code, num, price, bid_lookup[bid], "")
		print(e)
		
	def checkBalance(self):
		self.kiwoom.initOpw00018data()
		
		# request opw00001
		self.kiwoom.setInputValue("계좌번호", "8087071611")
		self.kiwoom.setInputValue("비밀번호", self.account[1])
		self.kiwoom.commRqData("opw00001_req", "opw00001", 0, "2000")
		
		# request opw00018
		self.kiwoom.setInputValue("계좌번호", "8087071611")
		self.kiwoom.setInputValue("비밀번호", self.account[1])
		self.kiwoom.commRqData("opw00018_req", "opw00018", 0, "2000")
		
		while self.kiwoom.prev_next == '2':
			time.sleep(0.2)
			self.kiwoom.setInputValue("계좌번호", "8087071611")
			self.kiwoom.setInputValue("비밀번호", self.account[1])
			self.kiwoom.commRqData("opw00018_req", "opw00018", 0, "2000")
		
		# print balance at table
		item = QTableWidgetItem(self.kiwoom.opw00001_data)
		item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
		self.qtTrade_tableWidget.setItem(0, 0, item)
		
		for i in range(1, 6):
			item = QTableWidgetItem(self.kiwoom.opw00018_data['single'][i-1])
			item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
			self.qtTrade_tableWidget2.setItem(0, i, item)
		self.qtTrade_tableWidget.resizeRowsToContents()
		
		# print own stock items at table
		item_cnt = len(self.kiwoom.opw00018_data['multi'])
		self.qtTrade_tableWidget2.setRowCount(item_cnt)
		
		for i in range(item_cnt):
			row = self.kiwoom.opw00018_data['multi'][i]
			for j in range(len(row)):
				item = QTableWidgetItem(row[i])
				item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
				self.qtTrade_tableWidget2.setItem(i, j, item)
		self.qtTrade_tableWidget2.resizeRowsToContents()
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	app.exec_()