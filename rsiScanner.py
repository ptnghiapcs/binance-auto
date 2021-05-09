from binance_api import socket_master, rest_master
import logging
import sys
import time
import technical_indicators as TC
import json
import math
import datetime
from orderCreator import sendOrder

try:
    symbolFile = open("symbols.json", "r")
except IOError:
    print("symbols.json NOT FOUND")
    quit()

loadedSymbols = json.load(symbolFile)

LEVERAGE = {}
STEP_SIZE = {}
for symbol in loadedSymbols:
    LEVERAGE[symbol["symbol"]] = symbol["leverage"]
    STEP_SIZE[symbol["symbol"]] = symbol["stepSize"]

balance = 15

SYMBOL_LIST = []

SYMBOL_LIST = [symbol["symbol"] for symbol in loadedSymbols]
KLINE_NAMES = [sym.lower() + "@kline_5m" for sym in SYMBOL_LIST]
DEPTH_NAMES = [sym.lower() + "@depth10@100ms" for sym in SYMBOL_LIST]
MARK_NAMES =  [sym.lower() + "@markPrice@1s" for sym in SYMBOL_LIST]

candle_socket = socket_master.Binance_SOCK(KLINE_NAMES, isFuture=True)
rest_api = rest_master.Binance_REST(private_key="M3rVcyKwP1xNhQRTHJy1I6RmHqK4OHwFnbtGYsW18F4IorXavoSWCpGa3JmV3KNh",
                                    public_key="8fKELP10OY69D8Sq47DjnQv9GHrjjpgRsVXDt9p15O5k36r06aEGZfKinxKbv1ls")


print("Loading initial candles...")
start_time = time.time()
candle_socket.set_live_and_historic_combo(rest_api)
print("Loading finished in {:.4f} seconds , waiting for update".format(time.time() - start_time))



depth_socket = socket_master.Binance_SOCK(DEPTH_NAMES, isFuture=True)
mark_socket = socket_master.Binance_SOCK(MARK_NAMES, isFuture=True)
print("Loading initial depth...")
start_time = time.time()
depth_socket.set_live_and_historic_depth(rest_api)
mark_socket.set_live_and_historic_markPrice(rest_api)
print("Loading finished in {:.4f} seconds , waiting for update".format(time.time() - start_time))


######################
class Trades:
    def __init__(self, entry, side, symbol, enterTime):
        self.entry = entry
        self.side = side
        self.symbol = symbol
        self.status = "OPEN"
        self.enterTime = enterTime
        if (side == "LONG"):
            self.sl = entry * 0.95
            self.tp = entry * 1.01
        else:
            self.sl = entry * 1.05
            self.tp = entry * 0.99

        global balance
        amount =  balance / entry
        self.amount = amount
        global rest_api
        sendOrder(symbol, side, amount, entry, rest_api,sl=self.sl, tp=self.tp)
        
    def checkClose(self, currPrice):
        if (self.side == "LONG"):
            if (currPrice >= self.tp):
                print("{} LONG trade TP at: {}".format(self.symbol, currPrice))
                return True
            elif(currPrice <= self.sl):
                print("{} LONG trade SL at: {}".format(self.symbol, currPrice))
                return True
            else:
                return False
        else:
            if (currPrice <= self.tp):
                print("{} SHORT trade TP at: {}".format(self.symbol, currPrice))
                return True
            elif(currPrice >= self.sl):
                print("{} SHORT trade SL at: {}".format(self.symbol, currPrice))
                return True
            else:
                return False
    def forceClose(self,currPrice):
        self.status = "CLOSED"
        priceMove = ((currPrice - self.entry) / self.entry) * 100
        if (self.entry < currPrice):
            if (self.side == "LONG"):
                print("{} LONG trade profit {:.3f}%, curr bid: {}".format(symbol, priceMove, currPrice))
            else:
                print("{} SHORT trade loss {:.3f}%, curr bid: {}".format(symbol, priceMove, currPrice))
        else:
            if (self.side == "LONG"):
                print("{} LONG trade loss {:.3f}%, curr ask: {}".format(symbol, priceMove, currPrice))
            else:
                print("{} SHORT trade profit {:.3f}%, curr ask: {}".format(symbol, priceMove, currPrice))




######################

trades = []
candle_socket.start()
depth_socket.start()
mark_socket.start()
cooldown = {}
timeOut = {}

for symbol in SYMBOL_LIST:
    cooldown[symbol] = 0
    timeOut[symbol] = 0

while(1):
    data = candle_socket.get_live_candles()
    markPrice = mark_socket.get_live_markPrice()
    

    newTrades = []

    for symbol in cooldown:
        cooldown[symbol] = 0

    for trade in trades:
        if (trade.status == "CLOSED"):
            continue
        if ((markPrice[trade.symbol]["time"] > trade.enterTime) and (not trade.checkClose(markPrice[trade.symbol]["markPrice"]))):
            newTrades.append(trade)
            cooldown[trade.symbol] = trade.enterTime

    trades = newTrades
    for symbol in data:
        candles = data[symbol]
        close = [candle[4] for candle in candles]
        rsi = TC.get_RSI(close)
        if ((rsi[0] >= 88 and rsi[1] >= 85) and (candles[0][0] > timeOut[symbol])):
            depth = depth_socket.get_live_depths(symbol=symbol)
            trade = Trades(depth['b'][-1][0], "SHORT", symbol, candles[0][0]) 
            print("{} RSI: {}, enter SHORT, entry: {}".format(symbol, rsi[0], trade.entry))
            trades.append(trade)
            cooldown[symbol] = candles[0][0]
            timeOut[symbol] = candles[0][0]
        elif ((rsi[0] <= 12 and rsi[1] <=15) and (candles[0][0] > timeOut[symbol])):
            depth = depth_socket.get_live_depths(symbol=symbol)
            trade = Trades(depth['a'][-1][0], "LONG", symbol, candles[0][0])
            print("{} RSI: {}, enter LONG, entry: {}".format(symbol, rsi[0], trade.entry))
            trades.append(trade)
            cooldown[symbol] = candles[0][0]
            timeOut[symbol] = candles[0][0]
        elif (rsi[1] <= 65 and (cooldown[symbol] > 0)):
            depth = depth_socket.get_live_depths(symbol=symbol)
            total = 0
            for trade in trades:
                if (trade.symbol == symbol and trade.side == "SHORT"):
                    trade.forceClose(depth['a'][-1][0])
                    total+=trade.amount
            sendOrder(symbol, "LONG",total, depth['a'][-1][0], rest_api)
        elif (rsi[1] >= 35 and (cooldown[symbol] > 0)):
            depth = depth_socket.get_live_depths(symbol=symbol)
            total = 0
            for trade in trades:
                if (trade.symbol == symbol and trade.side == "LONG"):
                    trade.forceClose(depth['b'][-1][0])
                    total+=trade.amount
            sendOrder(symbol, "SHORT",total, depth['b'][-1][0], rest_api)
    time.sleep(0.1)