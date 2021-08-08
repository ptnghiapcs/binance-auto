from binance_api import rest_master
import json
from collections import deque


rest_api = rest_master.Binance_REST()
candles = []
 

#start = 1620064860000 
start = 1626480000000 - (999*3600*1000)
# target = 1609459200000
endTime = start
file = open("rawTest.json",'w')
timeStampSave = {}
savedCandle = []

for i in range(31):
    result = rest_api.get_candles(symbol='BTCUSDT', interval='1h',startTime=str(start),limit='1000')
    #candles.extendleft(result)
    #print(result[-1][0], result[0][0])

    result.reverse()
    

    savedCandle.append(result)

    start = start - (1000*3600*1000)



#print(savedCandle)

for period in reversed(savedCandle):
    for candle in period:
        if (candle[0] not in timeStampSave):
            candles.append(candle)
            timeStampSave[candle[0]] = 1

print(len(candles))



#check order

for i in range(1,len(candles)):
    if (candles[i][0] < candles[i-1][0]):   
        print(i)
        j = i-1
        print("Bad order")
        while(candles[i][0] < candles[j][0]):
            print(j , candles[j][0])
            j =  j -1
        
        
for i in range(1,len(candles)):
    if (candles[i][0] - candles[i-1][0] > 3600*1000):   
        print(candles[i][0] - candles[i-1][0])


# candles = rest_api.get_candles(symbol='BTCUSDT', interval='5m', endTime='160961580 0000')
# print(len(candles)) 
# print(candles[0][0], candles[1][0])
# candles2 = rest_api.get_candles(symbol='BTCUSDT', interval='5m', endTime=str(candles[499][0]))
# print(candles2[0][0], candles2[1][0])

json.dump(list(candles), file)