"""
File Name   : pytrader.py
Author      : Spike Lee
Date        : 2017.01.21

Load UI and handle events
"""

import sys
from PyQt5.QtGui import *
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
		
		# timer
		self.timer = QTimer(self)
		self.timer.start(1000)
		self.timer.timeout.connect(self.timeout)
		
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
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	app.exec_()