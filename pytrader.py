"""
File Name   : pytrader.py
Author      : Spike Lee
Date        : 2017.01.21

Load UI and handle events
"""

import sys
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
		
		# get account info
		account_cnt  = int(self.kiwoom.getLoginInfo("ACCOUNT_CNT"))
		account_no   = self.kiwoom.getLoginInfo("ACCNO")
		account_list = account_no.split(';')[0:account_cnt]
		
		# timer
		self.timer = QTimer(self)
		self.timer.start(1000)
		self.timer.timeout.connect(self.timeout)
		
		# Window forms
		self.qtOrder_comboBox_account.addItems(account_list)
		self.qtOrder_lineEdit_item.textChanged.connect(self.itemCodeChanged)
		self.qtOrder_pushButton_sendOrder.clicked.connect(self.sendOrder)
		
	# 시간 및 접속 정보 출력
	def timeout(self):
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
		
	# 종목명 한글출력
	def itemCodeChanged(self):
		code = self.qtOrder_lineEdit_item.text()
		name = self.kiwoom.getMasterCodeName(code)
		self.qtOrder_lineEdit_code.setText(name)
		
	# 수동주문
	def sendOrder(self):
		order_type_lookup = {"신규매수":1, "신규매도":2, "매수취소":3, "매도취소":4}
		bid_lookup        = {"지정가":"00", "시장가":"03"}
		
		account     = self.qtOrder_comboBox_account.currentText()
		order_type  = self.qtOrder_comboBox_order.currentText()
		code        = self.qtOrder_lineEdit_item.text()
		bid         = self.qtOrder_comboBox_type.currentText()
		num         = self.qtOrder_spinBox_qty.value()
		price       = self.qtOrder_spinBox_price.value()
		
		self.kiwoom.sendOrder("sendOrder_req", "0101", account, order_type_lookup[order_type], code, num, price, bid_lookup[bid], "")
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	app.exec_()