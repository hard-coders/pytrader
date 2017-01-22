"""
File Name   : Kiwoom.py
Author      : Spike Lee
Date        : 2017.01.21

Kiwoom class for Kiwoom OpenAPI+
To use OpenAPI+, It inherited QAxWidget class.

'Tr' used in this project means transaction not trade.

Diff between OpenAPI+ and Kiwoom class
	- Naming of methods
		Chejan -> Trade
	- Naming of arguments
		str -> s
		Scr -> Screen
		Jongmok -> Item
		Gubun -> TradeType
		Hoga -> Bid     *I used this word same as 'asked' price
"""

import sys
import time
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
		
		# variables
		self.login_event_loop = None
		self.tr_event_loop = None
		self.prev_next = None
		
		# signal & slot
		self.OnEventConnect.connect(self.onEventConnect)
		self.OnReceiveTrData.connect(self.onReceiveTrData)
		self.OnReceiveChejanData.connect(self.onReceiveTradeData)
		
	
	""" ======= METHODS ======= """
	# set OHLC data form
	def initOHLCRawData(self):
		self.ohlc = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[]}
		
	# change string to currency format
	def changeFormat(self, data, percent = 0):
		is_minus = False
		
		if data.startswith('-'):
			is_minus = True
			
		strip_str = data.lstrip('-0')
		
		if strip_str == '':
			if percent == 1:
				return '0.00'
			else:
				return '0'
			
		if percent == 1:
			ret = format(int(strip_str) / 100, ',.2f')
		elif percent == 2:
			ret = format(float(strip_str), ',.2f')
		else:
			ret = format(int(strip_str), ',.d')
			
		if ret.startswith('.'):
			ret = '0' + ret
		if is_minus:
			ret = '-' + ret
			
		return ret
	
	def initOpw00018data(self):
		self.opw00018_data = {'single': [], 'multi': []}
	
	""" ======= OpenAPI+ METHODS ======= """
	# execute login window
	def commConnect(self):
		self.dynamicCall("CommConnect()")
		
		self.login_event_loop = QEventLoop()
		self.login_event_loop.exec_()
		
	# tr을 서버로 송신
	# nPrevNext : 조회("0"), 연속("2")
	def commRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
		self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, nPrevNext, sScreenNo)
		
		self.tr_event_loop = QEventLoop()
		self.tr_event_loop.exec_()

	# get user info via sTag
	def getLoginInfo(self, sTag):
		ret = self.dynamicCall("GetLoginInfo(QString)", sTag)
		return ret
	
	# send order to server
	def sendOrder(self, sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo):
		self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo])
	
	# transmit input transaction to server
	def setInputValue(self, sID, sValue):
		self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)
	
	# Tran 데이터, 실시간 데이터, 체결잔고 데이터 반환
	def commGetData(self, sItemCode, sRealType, sFieldName, nIndex, sInnerFieldName):
		ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sItemCode, sRealType, sFieldName, nIndex, sInnerFieldName)
		return ret.strip()
	
	# 화면 내 모든 리얼데이터 요청을 제거
	def disconnectRealData(self, sScreenNo):
		pass
	
	# 레코드 반복횟수 반환
	def getRepeatCnt(self, sTrCode, sRecordName):
		ret = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)
		return ret
	
	# 시장구분에 따른 종목코드 반환
	def getCodeListByMarket(self, sMarket):
		ret = self.dynamicCall("GetCodeListByMarket(QString)", sMarket)
		item_code = ret.split(';')
		return item_code
	
	# 현재 접속상태 반환
	def getConnectState(self):
		ret = self.dynamicCall("GetConnectState()")
		return ret
	
	# 종목코드의 한글명 반환
	def getMasterCodeName(self, sItemCode):
		ret = self.dynamicCall("GetMasterCodeName(QString)", sItemCode)
		return ret
	
	# 종목코드의 상장주식수를 반환
	def getMasterListedStockCnt(self, sItemCode):
		pass
	
	# 수신 데이터 바환
	def getCommData(self, sTrCode, sRecordName, nIndex, sItemName):
		pass
	
	# 체결잔고 데이터 반환
	def getTradeData(self, nFid):
		ret = self.dynamicCall("GetChejanData(int)", nFid)
		return ret
	
	""" ======= OpenAPI+ EVENTS ======= """
	# 서버통신 후 데이터를 받은 시점을 알려준다
	def onReceiveTrData(self, sScreenNo, sRQname, sTrCode, sRecordName, sPrevNext):
		self.prev_next = sPrevNext

		# opt10001 : tran 데이터 저장
		if sRQname == "opt10081_req":
			cnt = self.getRepeatCnt(sTrCode, sRQname)
			
			for i in range(cnt):
				date    = self.commGetData(sTrCode, "", sRQname, i, "일자")
				open    = self.commGetData(sTrCode, "", sRQname, i, "시가")
				high    = self.commGetData(sTrCode, "", sRQname, i, "고가")
				low     = self.commGetData(sTrCode, "", sRQname, i, "저가")
				close   = self.commGetData(sTrCode, "", sRQname, i, "현재가")
				
				self.ohlc['date'].append(date)
				self.ohlc['open'].append(int(open))
				self.ohlc['high'].append(int(high))
				self.ohlc['low'].append(int(low))
				self.ohlc['close'].append(int(close))
		# opw00001 : 예수금 정보
		elif sRQname == "opw00001_req":
			estimated_day2_deposit = self.commGetData(sTrCode, "", sRQname, 0, "d+2추정예수금")
			estimated_day2_deposit = self.changeFormat(estimated_day2_deposit)
			self.opw00001_data = estimated_day2_deposit
		# opw00018 : 계좌평가잔고내역 (한 번의 TR요청으로 최대 20개 보유 종목 가져옴)
		elif sRQname == "opw00018_req":
			# single data
			single_data = []
			
			total_purchase_price = self.commGetData(sTrCode, "", sRQname, 0, "총매입금액")
			single_data.append(self.changeFormat(total_purchase_price))
			
			total_eval_price = self.commGetData(sTrCode, "", sRQname, 0, "총평가금액")
			single_data.append(self.changeFormat(total_eval_price))
			
			total_eval_profit_loss_price = self.commGetData(sTrCode, "", sRQname, 0, "총평가손익금액")
			single_data.append(self.changeFormat(total_eval_profit_loss_price))
			
			total_profit_rate = self.commGetData(sTrCode, "", sRQname, 0, "총수익률(%)")
			single_data.append(self.changeFormat(total_profit_rate, 1))
			
			estimated_deposit = self.commGetData(sTrCode, "", sRQname, 0, "추정예탁자산")
			single_data.append(self.changeFormat(estimated_deposit))
			
			self.opw00018_data['single'] = single_data
			
			# multi data
			cnt = self.getRepeatCnt(sTrCode, sRQname)
			for i in range (cnt):
				multi_data = []
				
				item_name = self.commGetData(sTrCode, "", sRQname, i, "종목명")
				multi_data.append(item_name)
				
				quantity = self.commGetData(sTrCode, "", sRQname, i, "보유수량")
				multi_data.append(self.changeFormat(quantity))
				
				purchase_price = self.commGetData(sTrCode, "", sRQname, i, "매입가")
				multi_data.append(self.changeFormat(purchase_price))
				
				current_price = self.commGetData(str, "", sRQname, i, "현재가")
				multi_data.append(self.changeFormat(current_price))
				
				eval_profit_loss_price = self.commGetData(sTrCode, "", sRQname, i, "평가손익")
				multi_data.append(self.changeFormat(eval_profit_loss_price))
				
				profit_rate = self.commGetData(sTrCode, "", sRQname, i, "수익률(%)")
				multi_data.append(self.changeFormat(profit_rate, 2))
				
				self.opw00018_data['multi'].append(multi_data)
		self.tr_event_loop.exit()

	# 실시간 데이터를 받은 시점을 알려준다
	def onReceiveRealData(self, sItemCode):
		pass
	
	# 서버통신 후 메시지를 받은 시점을 알려준다
	def onReceiveMsg(self, sScrNo, sRQname, sTrCode, sMsg):
		pass
	
	# 체결데이터를 받은 시점을 알려준다
	def onReceiveTradeData(self, sTradeType, nItemCnt, sFidList):
		print("sTradeType : ", sTradeType)
		print(self.getTradeData(9203))
		print(self.getTradeData(302))
		print(self.getTradeData(900))
		print(self.getTradeData(909))
	
	# server connection event
	def onEventConnect(self, nErrCode):
		if nErrCode == 0:
			print("connected")
		else:
			print("disconnected")
			
		self.login_event_loop.exit()
		
	# 조건검색 실시간 편입, 이탈 종목을 받을 시점을 알려준다
	# sType                 : 편입("I"), 이탈("D")
	def onReceiveCondition(self, sItemCode, sType, sConditionName, sConditionIndex):
		pass
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	kiwoom = Kiwoom()
	kiwoom.commConnect()
	kiwoom.initOHLCRawData()
	
	kiwoom.initOpw00018data()