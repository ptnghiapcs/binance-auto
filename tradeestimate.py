import random

initMoney = 500

balance = initMoney
lastMilestone = initMoney
tradeBalance = initMoney
lastTradeMilestone = initMoney
trades = 0
risk = 0.01
reward = 0.015
moneyOut = 0

while (balance + moneyOut < 5000):
    tradeRes = random.randrange(100)
    if (tradeRes < 67):
        balance += tradeBalance*reward
    else:
        balance -= tradeBalance*risk
    
    if (balance - lastTradeMilestone >= 400):
        tradeBalance = min(tradeBalance+200, 20000)
        lastMilestone += 400
        moneyOut += 200
        balance -= 200
        print("Money out: {} after {} trades".format(moneyOut, trades))
        #print("Trades to double: {}, currMilestone: {}".format(trades-lastTradeMilestone,lastMilestone))
        #lastTradeMilestone = trades
    #print(balance)
    trades += 1

print("Reach target after: {} trades".format(trades))
print("Years if 1 trade per day: {}".format(trades/365))
print("Years if 3 trade per day: {}".format(trades/(365*3)))
print("Years if 5 trade per day: {}".format(trades/(365*5)))
#print("Years if 10 trade per day: {}".format(trades/(365*10)))

