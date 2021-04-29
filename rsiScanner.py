from binance_api import socket_master, rest_master
import logging
import sys
import time
import technical_indicators as TC
import json
import math
import datetime


try:
    symbolFile = open("symbols.json", "r")
except IOError:
    print("symbols.json NOT FOUND")
    quit()

loadedSymbols = json.load(symbolFile)

SYMBOL_LIST = []

SYMBOL_LIST = [symbol["symbol"] for symbol in loadedSymbols]
KLINE_NAMES = [sym.lower() + "@kline_1m" for sym in SYMBOL_LIST]


candle_socket = socket_master.Binance_SOCK(KLINE_NAMES, isFuture=True)
rest_api = rest_master.Binance_REST()


print("Loading initial candles...")
start_time = time.time()
candle_socket.set_live_and_historic_combo(rest_api)
print("Loading finished in {:.4f} seconds , waiting for update".format(time.time() - start_time))


######################
class Trades:
    def __init__(self, entry, side, symbol):
        self.entry = entry
        self.side = side
        self.symbol = symbol
        if (side == "LONG"):
            self.sl = entry * 0.99
            self.tp = entry * 1.01
        else:
            self.sl = entry * 1.01
            self.tp = entry * 0.99
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


######################

trades = []
candle_socket.start()
cooldown = {}

for symbol in SYMBOL_LIST:
    cooldown[symbol] = 0

while(1):
    data = candle_socket.get_live_candles()
    newTrades = []
    for trade in trades:
        if ( not trade.checkClose(data[trade.symbol][0][4])):
            newTrades.append(trade)
    trades = newTrades
    for symbol in data:
        candles = data[symbol]
        close = [candle[4] for candle in candles]
        rsi = TC.get_RSI(close)
        if ((rsi[0] >= 85) and (cooldown[symbol]==0)):
            print("{} RSI: {}".format(symbol, rsi[0]))
            trade = Trades(candles[0][4], "SHORT", symbol) 
            trades.append(trade)
            cooldown[symbol] = 1
            print(cooldown[symbol])
        elif ((rsi[0] <= 15 )and (cooldown[symbol]==0)):
            print("{} RSI: {}".format(symbol, rsi[0]))
            trade = Trades(candles[0][4], "LONG", symbol)
            trades.append(trade)
            cooldown[symbol] = 1
            print(cooldown[symbol])
        else:
            cooldown[symbol] = 0
    time.sleep(0.1)