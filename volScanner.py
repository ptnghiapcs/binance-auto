from binance_api import socket_master, rest_master
import logging
import sys
import time
import technical_indicators as TC
import curses

stdscr = curses.initscr()


SYMBOL_LIST = ["btc","eth"]
STREAM_NAMES = [sym + "usdt@kline_1m" for sym in SYMBOL_LIST]
SYMBOL_NAMES = [sym + "usdt" for sym in SYMBOL_LIST]


class Symbol:
    def __init__(self):
        self.Vol50EMA   = 0
        self.currentTick = 0
        self.lastPrice = 0
    def updateData(self, candles):
        self.currentTick = candles[0][0]
        vols = [a[5] for a in candles]
        self.Vol50EMA = TC.get_EMA(vols, 50)


#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
def main(stdscr):
    symbols = {}

    for sym in SYMBOL_NAMES:
        symbols[sym] = Symbol()

    socket = socket_master.Binance_SOCK(STREAM_NAMES)
    rest_api = rest_master.Binance_REST()

    socket.set_live_and_historic_combo(rest_api)

    socket.start()

    while(1):
        data = socket.get_live_candles()
        for symbol in data:
            candles = data[symbol]
            currSymbol = symbols[symbol]
            if (candles[0][0] > currSymbol.currentTick):
                currSymbol.updateData(candles)
            # if (currSymbol[0][5] )

        time.sleep(1)

curses.wrapper(main)