from binance_api import rest_master
import json
from collections import deque

rest_api = rest_master.Binance_REST()
candles = deque()
 

start = 1546300800000 
target = 1609459200000
endTime = start
file = open("btc_1min.json",'w')

for i in range(1000):
    result = rest_api.get_candles(symbol='BTCUSDT', interval='1m', startTime=str(start),limit='1000')
    candles.extendleft(result)
    endTime = result[-1][0] 
    start = endTime + (1*60*1000)


# candles = rest_api.get_candles(symbol='BTCUSDT', interval='5m', endTime='160961580 0000')
# print(len(candles)) 
# print(candles[0][0], candles[1][0])
# candles2 = rest_api.get_candles(symbol='BTCUSDT', interval='5m', endTime=str(candles[499][0]))
# print(candles2[0][0], candles2[1][0])

json.dump(list(candles), file)