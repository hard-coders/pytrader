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
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	app.exec_()