"""
File Name   : autologin.py
Author      : Spike Lee
Date        : 2017.01.21


"""

from pywinauto import application
from pywinauto import timings
import time
import os

# Account Info
account = []
with open("account.txt", 'r') as f:
	account = f.readlines()

# 번개 실행
app = application.Application()
app.start("C:/Kiwoom/KiwoomFlash2/khministarter.exe")

title = "번개 Login"
dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))

pass_ctrl = dlg.Edit2
pass_ctrl.SetFocus()
pass_ctrl.TypeKeys(account[0])

cert_ctrl = dlg.Edit3
cert_ctrl.SetFocus()
cert_ctrl.TypeKeys(account[1])

btn_ctrl = dlg.Button0
btn_ctrl.Click()

# 대기 후 종료
time.sleep(50)
os.system("taskkill /im khmini.exe")