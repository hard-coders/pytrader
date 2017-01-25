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
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

class Kiwoom(QAxWidget):
	def __init__(self):
		super().__init__()
		self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
		
		# variables
		self.login_event_loop   = None
		self.tr_event_loop      = None
		self.prev_next          = None
		self.ohlc               = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[]}
		self.opw00001_data      = ""
		self.opw00018_data      = {'single': [], 'multi': []}
		
		# signal & slot
		self.OnEventConnect.connect(self.onEventConnect)
		self.OnReceiveTrData.connect(self.onReceiveTrData)
		self.OnReceiveChejanData.connect(self.onReceiveTradeData)
		
	""" ======= METHODS ======= """
	def changeFormat(self, strData, percent = 0):
		"""
		Change string to currency format
		:param strData: 바꿀 문자열
		:param percent: 0=정수, 1=소수점, 2=백분율
		"""
		is_minus = False
		
		if strData.startswith('-'):
			is_minus = True
		
		strip_str = strData.lstrip('-0')
		
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
			ret = format(int(strip_str), ',d')
		
		if ret.startswith('.'):
			ret = '0' + ret
		if is_minus:
			ret = '-' + ret
		
		return ret
	
	""" ======= OpenAPI+ METHODS ======= """
	def commConnect(self):
		""" execute login window """
		self.dynamicCall("CommConnect()")
		
		self.login_event_loop = QEventLoop()
		self.login_event_loop.exec_()
	
	def commRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
		"""
		transmit Transaction to server
		:param nPrevNext: 0=조회, 2=연속
		"""
		self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, nPrevNext, sScreenNo)
		self.tr_event_loop = QEventLoop()
		self.tr_event_loop.exec_()
	
	def getLoginInfo(self, sTag):
		ret = self.dynamicCall("GetLoginInfo(QString)", sTag)
		return ret
	
	def sendOrder(self, sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo):
		ret = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",[sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo])
		print("SEND ORDER ERROR : " + str(ret))
		return ret
	
	def setInputValue(self, sID, sValue):
		self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)
	
	def commGetData(self, sItemCode, sRealType, sFieldName, nIndex, sInnerFieldName):
		"""
		- Transaction 데이터
		:param sItemCode        : Tr명
		:param sRealType        : not used
		:param sFieldName       : 레코드 명
		:param nIndex           : 반복 인뎃스
		:param sInnerFieldName  : 아이템 명
		
		- 실시간 데이터
		:param sItemCode        : Key Code
		:param sRealType        : Real Type
		:param sFieldName       : Item Index
		:param nIndex           : not used
		:param sInnerFieldName  : not used
		
		- 체결잔고 데이터
		:param sItemCode        : 체결구분
		:param sRealType        : "-1"
		:param sFieldName       : not used
		:param nIndex           : Item Index
		:param sInnerFieldName  : not used
		"""
		ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sItemCode, sRealType, sFieldName, nIndex, sInnerFieldName)
		return ret.strip()
	
	def disconnectRealData(self, sScreenNo):
		pass
	
	def getRepeatCnt(self, sTrCode, sRecordName):
		""" 레코드 반복 횟수 리턴"""
		ret = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)
		return ret
	
	def getCodeListByMarket(self, sMarket):
		""" 시장구분에 따른 종목코드 리턴"""
		ret = self.dynamicCall("GetCodeListByMarket(QString)", sMarket)
		item_code = ret.split(';')
		return item_code
	
	def getConnectState(self):
		ret = self.dynamicCall("GetConnectState()")
		return ret
	
	def getMasterCodeName(self, sItemCode):
		""" 종목코드 한글명 리턴 """
		ret = self.dynamicCall("GetMasterCodeName(QString)", sItemCode)
		return ret
	
	def getMasterListedStockCnt(self, sItemCode):
		""" 종목코드의 상장주식 수를 리턴"""
		pass
	
	def getCommData(self, sTrCode, sRecordName, nIndex, sItemName):
		"""
		cf) commGetData
		개발가이드에서 CommGetData보다 제약이 적은 GetCommData를 쓰라고 명시
		ex)현재가출력 : openAPI.GetCommData("opt00001_req", "주식기본정보", 0, "현재가")
		"""
		ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, nIndex, sItemName)
		return ret
	
	def getTradeData(self, nFid):
		""" 체결잔고 데이터 리턴"""
		ret = self.dynamicCall("GetChejanData(int)", nFid)
		return ret
	
	"""
	======= OpenAPI+ EVENT FUNCTIONS
        시세조회나 조건검색요청등 서버에 데이터를 요청해서 키움OpenAPI가 데이터를 수신하게 되면 사용자 프로그램에 특정함수를 자동으로 호출해서 알려줍니다.
        이렇게 어떤 조건이 맞으면 키움OpenAPI에서 자동으로 호출해서 알려주며 OnReceiveTRData(), OnEventConnect(), OnReceiveRealData()
        처럼 함수이름 앞에 On~이 붙어있어서 일반적인 함수와 구별됩니다.
        로그인, 시세조회, 주문등 각 요청별로 요청함수, 이벤트와 데이터획득함수가 분류되어 있으니 용도에 맞는 함수를 사용해야 합니다.
	"""
	def onReceiveTrData(self, sScreenNo, sRQname, sTrCode, sRecordName, sPrevNext, notUsed1, notUsed2, notUsed3, notUsed4):
		"""
		서버로부터 event를 받으면 자동 실행된다.
		수신 받은 데이터는 commGetData()를 통해 받는다.
		GetCommData()를 쓰라고 하는데 자세한건 나중에 수정
		"""
		self.prev_next = sPrevNext
		print("RqName : " + sRQname)
		print("Trcode : " + sTrCode + "\n")
		# opt10001 : tran 데이터 저장
		# if sRQname == "opt10001_req":
		# 	cnt = self.getRepeatCnt(sTrCode, sRQname)
		#
		# 	for i in range(cnt):
		# 		date    = self.commGetData(sTrCode, "", sRQname, i, "일자")
		# 		open    = self.commGetData(sTrCode, "", sRQname, i, "시가")
		# 		high    = self.commGetData(sTrCode, "", sRQname, i, "고가")
		# 		low     = self.commGetData(sTrCode, "", sRQname, i, "저가")
		# 		close   = self.commGetData(sTrCode, "", sRQname, i, "현재가")
		#
		# 		self.ohlc['date'].append(date)
		# 		self.ohlc['open'].append(int(open))
		# 		self.ohlc['high'].append(int(high))
		# 		self.ohlc['low'].append(int(low))
		# 		self.ohlc['close'].append(int(close))
		if sRQname == "opw00001_req":   # opw00001 : 예수금상세현황요청
			estimated_day2_deposit = self.commGetData(sTrCode, "", sRQname, 0, "d+2추정예수금")
			self.opw00001_data = self.changeFormat(estimated_day2_deposit)
		elif sRQname == "opw00018_req": # opw00018 : 계좌평가잔고내역
			"""
			single : 개별
			multi : 개별합산
			한 번의 TR요청으로 최대 20개 보유 종목 가져옴
			"""
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
				
				current_price = self.commGetData(sTrCode, "", sRQname, i, "현재가")
				multi_data.append(self.changeFormat(current_price))
				
				eval_profit_loss_price = self.commGetData(sTrCode, "", sRQname, i, "평가손익")
				multi_data.append(self.changeFormat(eval_profit_loss_price))
				
				profit_rate = self.commGetData(sTrCode, "", sRQname, i, "수익률(%)")
				multi_data.append(self.changeFormat(profit_rate, 2))
				
				self.opw00018_data['multi'].append(multi_data)
		self.tr_event_loop.exit()
		
	def onReceiveRealData(self, sItemCode):
		pass
	
	def onReceiveMsg(self, sScrNo, sRQname, sTrCode, sMsg):
		pass
	
	def onReceiveTradeData(self, sTradeType, nItemCnt, sFidList):
		print("sTradeType : ", sTradeType)
		print(self.getTradeData(9203))
		print(self.getTradeData(302))
		print(self.getTradeData(900))
		print(self.getTradeData(909))
	
	def onEventConnect(self, nErrCode):
		if nErrCode == 0:
			print("connected")
		else:
			print("disconnected")
		
		self.login_event_loop.exit()
	
	def onReceiveCondition(self, sItemCode, sType, sConditionName, sConditionIndex):
		"""
		조건검색 실시간 편입, 이탈 종목을 받을 시점을 알려준다
		:param sItemCode:
		:param sType: 'I' = 편입, 'D' = 이탈
		:return:
		"""
		pass
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	kiwoom = Kiwoom()
	kiwoom.commConnect()
	app.exec_()