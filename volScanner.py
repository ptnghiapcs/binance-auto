from binance_api import socket_master, rest_master
import logging
import sys
import time
import technical_indicators as TC
import curses
import json
import math

stdscr = curses.initscr()


try:
    symbolFile = open("symbols.json", "r")
except IOError:
    print("symbols.json NOT FOUND")
    quit()

loadedSymbols = json.load(symbolFile)

try:
    configFile = open("scanner_config.json", "r")
except IOError:
    print("scanner_config.json NOT FOUND")
    quit()

CONFIG = json.load(configFile)
CONFIG["daily_percent"] = float(CONFIG["daily_percent"].replace("%",""))/100
CONFIG["price_move_threshold"] = float(CONFIG["price_move_threshold"].replace("%",""))/100

#print(CONFIG)


SYMBOL_LIST = []

if (CONFIG["use_full_symbols"]):
    SYMBOL_LIST = [symbol["symbol"] for symbol in loadedSymbols]
else:
    SYMBOL_LIST = CONFIG["symbols"]

KLINE_NAMES = [sym.lower() + "@kline_1m" for sym in SYMBOL_LIST]
TICKER_NAMES = [sym.lower() + "@miniTicker" for sym in SYMBOL_LIST]

STREAM_NAMES = KLINE_NAMES
STREAM_NAMES.extend(TICKER_NAMES)

class Symbol:
    def __init__(self):
        self.Vol50EMA   = 0
        self.currentTick = 0
        self.lastPrice = 0
        self.spike = False
        self.lastVol = 0
    def updateData(self, candles):
        self.currentTick = candles[0][0]
        self.lastVol = candles[1][7]
        if (self.spike):
            if (candles[1][7] < candles[2][7]):
                self.spike = False
    def setSpike(self):
        self.spike = True


#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
def main(stdscr):
    symbols = {}

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    for sym in SYMBOL_LIST:
        symbols[sym] = Symbol()

    socket = socket_master.Binance_SOCK(STREAM_NAMES, isFuture=True)
    rest_api = rest_master.Binance_REST()


    stdscr.addstr("Loading initial candles...\n")
    stdscr.refresh()
    start_time = time.time()
    socket.set_live_and_historic_combo(rest_api)
    stdscr.addstr("Loading finished in {:.4f} seconds , waiting for update\n".format(time.time() - start_time))
    stdscr.refresh()

    curses.halfdelay(10)
    socket.start()

    while(1):
        data = socket.get_live_candles()
        tickers = socket.get_live_ticker()
        stdscr.move(0,0)
        spikeCount = 0
        for symbol in data:
            candles = data[symbol]
            ticker = tickers[symbol]
            currSymbol = symbols[symbol]
            if (candles[0][0] > currSymbol.currentTick):
                currSymbol.updateData(candles)
            # if (currSymbol[0][5] 
            degree = math.degrees(math.atan(candles[0][7]/candles[1][7] - 1))
            dayPercent = candles[0][7] / ticker['volume']
            priceMovment = abs(candles[0][4] - candles[0][1]) / candles[0][1]
            if ((degree >= CONFIG["slope"] and  dayPercent >= CONFIG["daily_percent"] and priceMovment >= CONFIG["price_move_threshold"]) or (currSymbol.spike)):
                spikeCount += 1
                stdscr.addstr(symbol + " volume spike degree: {:.2f}, price move: {:.5f}% \n".format(degree, priceMovment*100), curses.color_pair(1))
                currSymbol.setSpike()
            elif not(CONFIG["use_full_symbols"]):
                stdscr.addstr(symbol + " volume slope is: {:.2f}, daily percent is: {:.5f}%, price percent: {:.5f}% \n".format(degree, dayPercent*100, priceMovment*100),curses.color_pair(2))
                #stdscr.addstr(symbol + "volumes {:.2f} {:.2f}; 24hr:{:.2f}; price {:.5f} {:.5   f} \n".format(candles[0][7], candles[1][7], ticker['volume'], candles[0][4], candles[0][1]),curses.color_pair(2))

        # if (spikeCount == 0):
        #     stdscr.addstr("No spike found, current SUSHI price: {}, time {}".format(data['SUSHIUSDT'][0][4], data['SUSHIUSDT'][0][0]),curses.color_pair(2))
        c = stdscr.getch()
        if (c==ord('q')):
            socket.stop()
            quit()


curses.wrapper(main)