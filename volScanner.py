from binance_api import socket_master, rest_master
import logging
import sys
import time
import technical_indicators as TC
import json
import math
import datetime
from collections import deque
import heapq

SECONDS_IN_MIN = 60
FIRST_CHECK = 5 * SECONDS_IN_MIN
SECOND_CHECK = 30 * SECONDS_IN_MIN

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
for trigger in CONFIG["triggers"]:
    trigger["daily_percent"] = float(trigger["daily_percent"].replace("%",""))/100
    trigger["price_move_threshold"] = float(trigger["price_move_threshold"].replace("%",""))/100

#print(CONFIG)


SYMBOL_LIST = []

if (CONFIG["use_full_symbols"]):
    SYMBOL_LIST = [symbol["symbol"] for symbol in loadedSymbols]
else:
    SYMBOL_LIST = CONFIG["symbols"]

KLINE_NAMES = [sym.lower() + "@kline_1m" for sym in SYMBOL_LIST]
TICKER_NAMES = [sym.lower() + "@miniTicker" for sym in SYMBOL_LIST]

# STREAM_NAMES = KLINE_NAMES
# STREAM_NAMES.extend(TICKER_NAMES)
##########################
class Symbol:
    def __init__(self):
        self.currentTick = 0
        self.prevVol = 0
        self.spike = False
        self.currVol = 0
    def updateData(self, currTick, currVolume):
        self.currentTick = currTick
        if (self.currVol < self.prevVol):
            self.spike = False
        self.prevVol = self.currVol
        self.currVol = currVolume
    def updateCurrVol(self, newVol):
        self.currVol = newVol
    def setSpike(self):
        self.spike = True

###########################
class PriceTrack:
    def __init__(self, symbol, startPrice, timestamp, triggerIdx, waitDuration):
        self.symbol = symbol
        self.startPrice = startPrice
        self.waitDuration = waitDuration
        duration = 0
        if ('30' in waitDuration):
            duration = SECOND_CHECK
        else:
            duration = FIRST_CHECK
        self.checkTime = timestamp + duration
        self.triggerIdx = triggerIdx
    def getStr(self, currPrice):
        move_percent = (currPrice - self.startPrice) / self.startPrice * 100
        return ("{} {} after spike, price moved: {:.5f}%".format(self.symbol, self.waitDuration, move_percent))

##########################

class EventHeap(object):
    def __init__(self, initial=None, key=lambda x:x.checkTime):
        self.key = key
        self.index = 0
        if initial:
            self._data = [(key(item), i, item) for i, item in enumerate(initial)]
            self.index = len(self._data)
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, item):
        heapq.heappush(self._data, (self.key(item), self.index, item))
        self.index += 1

    def pop(self):
        return heapq.heappop(self._data)[2]
    def peak(self):
        return self._data[0][0]
    def isEmpty(self):
        return (len(self._data) == 0)

#########################
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
events = EventHeap()

def main():
    symbols = {}
    for i in range(len(CONFIG["triggers"])):
        symbols[i] = {}
        for sym in SYMBOL_LIST:
            symbols[i][sym] = Symbol()

    # curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    # curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    

    candle_socket = socket_master.Binance_SOCK(KLINE_NAMES, isFuture=True)
    ticker_socket = socket_master.Binance_SOCK(TICKER_NAMES, isFuture=True)
    rest_api = rest_master.Binance_REST()


    
    print("Loading initial candles...")
    start_time = time.time()
    candle_socket.set_live_and_historic_combo(rest_api)
    ticker_socket.set_live_and_historic_ticker(rest_api)
    print("Loading finished in {:.4f} seconds , waiting for update".format(time.time() - start_time))


    candle_socket.start()
    ticker_socket.start()

    while(1):
        data = candle_socket.get_live_candles()
        tickers = ticker_socket.get_live_ticker()
        outputs = {}
        for i in range(len(CONFIG["triggers"])):
            outputs[i] = []

        currTime = datetime.datetime.now()
        currStamp = time.time()
        if (not events.isEmpty()):
            while(events.peak() <= currStamp):  
                event = events.pop()
                outStr = currTime.strftime("%d/%m/%Y %H:%M") + event.getStr(data[event.symbol][0][4])
                outputs[event.triggerIdx].append(outStr + "\n")
                print("Condition {} :".format(event.triggerIdx) + outStr)

        for symbol in data:
            if (symbol not in tickers):
                continue
            candles = data[symbol]
            ticker = tickers[symbol]
            
            # if (currSymbol[0][5] 

            for idx, trigger in enumerate(CONFIG["triggers"]):

                currSymbol = symbols[idx][symbol]


                tf = trigger["time_frame"]
                currVolume = 0
                prevVolume = 0

                for i in range(tf):
                    currVolume += candles[i][7]
                for i in range(tf, tf*2):
                    prevVolume += candles[i][7]

                if (prevVolume == 0) or (currVolume == 0):
                    continue

                if (candles[0][0] > currSymbol.currentTick):
                    currSymbol.updateData(candles[0][0], currVolume)
                else:
                    currSymbol.updateCurrVol(currVolume)

                openPrice = candles[tf-1][1]
                currPrice = candles[0][4]
                
                try:
                    degree = math.degrees(math.atan(currVolume/prevVolume - 1))
                except ZeroDivisionError:
                    print(currVolume, prevVolume)
                    print(tf, tf*2)
                    print(candles[:tf*2])
                    quit()

                dayPercent = currVolume / ticker['volume']
                priceMovment = (currPrice - openPrice) / openPrice
                if ((degree >= trigger["slope"] and  dayPercent >= trigger["daily_percent"] and abs(priceMovment) >= trigger["price_move_threshold"]) and (not currSymbol.spike)):
                    output = currTime.strftime("%d/%m/%Y %H:%M") + " " + symbol + " degree: {:.2f}, price move: {:.5f}%, daily vol {:.5f}%".format(degree, priceMovment*100,dayPercent*100)
                    print("Condition: "+ str(idx) +": "+output)
                    outputs[idx].append(output+"\n")
                    currSymbol.setSpike()

                    five_min = PriceTrack(symbol, currPrice, currStamp, idx, "5 min")
                    thirty_min = PriceTrack(symbol, currPrice, currStamp, idx, "30 min")
                    events.push(five_min)
                    events.push(thirty_min)
                elif not(CONFIG["use_full_symbols"]):
                    pass
              
        for i in range(len(CONFIG["triggers"])):
            if (len(outputs[i])>0):
                file = open("trigger_"+str(i)+"_output.txt", "a")
                file.writelines(outputs[i])
                file.close()

        # if (spikeCount == 0):
        #     stdscr.addstr("No spike found, current SUSHI price: {}, time {}".format(data['SUSHIUSDT'][0][4], data['SUSHIUSDT'][0][0]),curses.color_pair(2))
        # c = stdscr.getch()
        # if (c==ord('q')):
        #     candle_socket.stop()
        #     quit()
main()