import technical_indicators as TC
import json
import matplotlib.pyplot as plt
import numpy as np


file = open("btc_15min.json","r")

prices = json.load(file)

l = len(prices)



candleDict = {} 
candleDict["open"] = [p[1] for p in prices]
candleDict["high"] = [p[2] for p in prices]
candleDict["low"]  = [p[3] for p in prices]
candleDict["close"] = [p[4] for p in prices]

ADX = TC.get_ADX_DI(candleDict, dataType="normal")

ema = TC.get_EMA(candleDict["close"],200)
MACD = TC.get_MACD(candleDict["close"])
ratio = 1.5
shortRatio = 3
 
#print(l, len(ema), len(MACD)) 

orderStatus = "FREE" 
stopLoss = 0
target = 0
wins = 0
loss = 0
printAt = 0
positionSize = 0


initMoney = 5000

balance = initMoney
lastMilestone = initMoney
lastTradeMilestone = initMoney
tradeBalance = initMoney
moneyOut = 0
riskRatio = 0.01
feeRate = 0.075 / 100
fee = 0
shortPeriod = 0
hourInterest = (0.03/100) / 24


# print(MACD[240], close[240])
# print(MACD[239], close[239])
# print(MACD[238], close[238])
# print(MACD[237], close[237])

smallStopLoss = 0



entryPrice = []
entryTime = []
targetPrice = []
stopLossPrice = []
winTime = []
loseTime = []
stopLosses = []
targets = []
total = []
gain = []
lose = []

for i, candle in reversed(list(enumerate(prices[:(l-202)]))):
    if ((wins+loss) % 100 == 0 and wins > printAt):
        print("Trade {} orders, win rate {}".format(wins+loss, wins/(wins+loss)))
        printAt = wins


    if (orderStatus == "FREE"):
        # if ((min(prices[i+1][1],prices[i+1][4]) > ema[i+1]) 
        # and (MACD[i+1]['macd'] < 0 and MACD[i+1]['signal'] < 0)
        # and (abs(MACD[i+1]['macd'] - MACD[i+1]['signal']) < abs(MACD[i+2]['macd'] - MACD[i+2]['signal']))
        # and ((MACD[i+1]['macd'] + (MACD[i+1]['macd'] - MACD[i+2]['macd'])) >= (MACD[i+1]['signal'] + (MACD[i+1]['signal'] - MACD[i+2]['signal'])))
        # #and (MACD[i+1]['hist'] > MACD[i+2]['hist'])
        # ):

        if ((prices[i+1][4] > ema[i+1])
        and (MACD[i+1]['macd'] < 0 and MACD[i+1]['signal'] < 0)
        and (MACD[i+1]['hist'] >= 0)
        and (MACD[i+2]['hist'] < 0)
        and (ADX[i+1]['ADX'] > 25)
        ):
            #Long position
            entry = prices[i+1][4] 

            past = min(i+10, l-200)
            stopLoss = prices[i+1][3]
            for j in range(i+1,past):
                stopLoss = min(stopLoss, prices[j][3])
            
            # if (stopLoss == prices[i+1][1]):
            #     stopLoss = stopLoss - (stopLoss * 0.01)
            # else:
            stopLoss = stopLoss - (stopLoss * 0.0008)

            diff = entry - stopLoss
            # if (diff/entry < 0.005):
            #     diff = entry*0.005
            #     stopLoss = entry - diff

            # if (diff/entry < 0.004):
            #     stopLoss = entry*(1-0.004)
            #     diff = entry - stopLoss

            target = entry + (diff*ratio)

            accountRisk = tradeBalance*riskRatio
            positionSize = accountRisk / diff
            #print(positionSize*entry)
            #print(diff/entry)

            if (positionSize * entry > balance):
                smallStopLoss += 1

            if (candle[3] <= entry and candle[2] >= entry):
                orderStatus = "LONG"
                targets.append(target)
                stopLosses.append(stopLoss)
                entryPrice.append(entry)
                entryTime.append(i+1)
                balance -= positionSize*entry
                positionSize -= positionSize*feeRate


                
                  
            # else:
            #     orderStatus = "WAIT"
            
        # if ((prices[i+1][4] < ema[i+1])
        # and (MACD[i+1]['macd'] > 0 and MACD[i+1]['signal'] > 0)
        # and (MACD[i+2]['macd'] > 0 and MACD[i+2]['signal'] > 0)
        # and (MACD[i+1]['macd'] <= MACD[i+1]['signal'])
        # and (MACD[i+2]['macd'] > MACD[i+2]['signal'])
        # ):
        #     #short position
        #     entry = prices[i+1][4]
        #     past = min(i+8, l-200)
        #     stopLoss = prices[i+1][2]

        #     for j in range(i+1,past):
        #         stopLoss = max(stopLoss, prices[j][2])

        #     stopLoss = stopLoss + (stopLoss * 0.001)

        #     diff = stopLoss - entry

        #     target = entry - (diff*ratio)

        #     accountRisk = tradeBalance*riskRatio
        #     positionSize = accountRisk / diff

        #     if(candle[2] >= entry and candle[3] <= entry):
        #         orderStatus = "SHORT"
        #         targets.append(target)
        #         stopLosses.append(stopLoss)
        #         entryPrice.append(entry)
        #         entryTime.append(i+1)
        #         balance += (positionSize*entry)*(1-feeRate)
            # else:
            #     orderStatus = "WAIT"

    # if (orderStatus == "WAITLONG"):
    #     if ((MACD[i]['macd'] >= MACD[i]['signal'])
    #        and (MACD[i+1]['macd'] < MACD[i+1]['signal'])
    #     ):
    #         orderStatus = "IN"
    #     else:
    #         orderStatus = "FREE"
    # if (orderStatus == "WAITSHORT"):
    #     if ((MACD[i]['macd'] <= MACD[i]['signal'])
    #        and (MACD[i+1]['macd'] > MACD[i+1]['signal'])
    #     ):
    #         orderStatus = "IN"
    #     else:
    #         orderStatus = "FREE"

    if (orderStatus == "LONG"):
        high = candle[2]
        low = candle[3]
        if (target <= high and target >= low):
            wins += 1
            orderStatus = "FREE"
            targetPrice.append(target)
            winTime.append(i)

            #print(positionSize, positionSize*target, positionSize*entry)
            balance += (positionSize*target)*(1-feeRate)
            gain.append(positionSize * (target-entry))

            #print(((target-entry)/entry) * 100, target,entry, positionSize*target)

            # if (balance - lastTradeMilestone >= 400):
            #     tradeBalance = min(tradeBalance+200, 5000)
            #     lastTradeMilestone += 400
            #     moneyOut += 200
            #     balance -= 200
            total.append(balance)
            positionSize = 0
            continue
        if (stopLoss <= high and stopLoss >= low):
            loss += 1
            orderStatus = "FREE"
            stopLossPrice.append(stopLoss)
            loseTime.append(i)
            
            balance += (positionSize*stopLoss)*(1-feeRate)
            lose.append(positionSize * (entry-stopLoss))
            total.append(balance)
            positionSize = 0
            continue


    if (orderStatus == "SHORT"):
        high = candle[2]
        low = candle[3]
        shortPeriod += 1
        if (target <= high and target >= low):
            wins += 1
            orderStatus = "FREE"
            targetPrice.append(target)
            winTime.append(i)

            totalInterest = (max(1,shortPeriod / 4)*hourInterest)*positionSize

            balance -= ((positionSize+totalInterest)/(1-feeRate))  * target
            shortPeriod = 0
            positionSize = 0
            #gain.append(entry*positionSize - (positionSize+totalInterest)/(1-feeRate) * target)

            total.append(balance)
            continue
        if (stopLoss <= high and stopLoss >= low):
            loss += 1
            orderStatus = "FREE"
            stopLossPrice.append(stopLoss)
            loseTime.append(i)
            totalInterest = (max(1,shortPeriod / 4)*hourInterest) * positionSize
            shortPeriod = 0
            balance -= ((positionSize+totalInterest)/(1-feeRate)) * stopLoss
            total.append(balance)
            lose.append(entry*positionSize - (positionSize+totalInterest)/(1-feeRate) * target)
            positionSize = 0
            continue
    

    # if (orderStatus == "WAIT"):
    #     print("Waiting on {} entry, high {}, low {}, target: {}, stopLoss: {}".format(entry, candle[2], candle[3],target,stopLoss))
    #     if (entry <= candle[2] and entry >= candle[3]):
    #         orderStatus = "IN"
    #         entryPrice.append(entry)
    #         entryTime.append(i)
    #     if ((target <= candle[2] and target >= candle[3]) or (stopLoss <= candle[2] and stopLoss >= candle[3])):
    #         print("Wait hit stop")
    #         orderStatus == "FREE"
# print(entryPrice)
# print(entryTime)


print("Total balance made: {}".format(total[-1]))   
print("Trade {} orders, win rate {}".format(wins+loss, wins/(wins+loss)))
#print(gain)
#print(lose)

fig, ax = plt.subplots()

# close.reverse()
# ema = np.flipud(ema)
# entryTime.reverse()

# dummy1 = [0]*200
# dummy2 = [0]*200

# dummy1.extend(entryPrice)
# dummy2.extend(entryTime)

# zeros = np.zeros(200)
# ema_new = np.append(zeros, ema)

# entryPrice.reverse()
ax.plot(candleDict["close"])
ax.plot(ema)
# ax.plot(lows,'co')
# ax.plot(highs,'co')
ax.plot(entryTime, entryPrice, 'bo')
ax.plot(entryTime, stopLosses, 'ko')
ax.plot(entryTime, targets, 'ko')
ax.plot(winTime, targetPrice, 'go')
ax.plot(loseTime, stopLossPrice, 'ro')


#ax.plot(total)
plt.show()


