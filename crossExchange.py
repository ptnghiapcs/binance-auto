from binance_api import socket_master, rest_master
from bybit import BybitWS, BybitREST
import time
import msvcrt
import json
from orderCreator import sendOrder, cancelOrder, queryOrder, sendMarketOrder

SYMBOL_LIST = ["BTCUSDT"]
BUSD = ["BTCBUSD"]
BINACE_DEPTH_NAMES = [sym.lower() + "@depth5@100ms" for sym in BUSD]
BYBIT_DEPTH_NAMES = ["orderBookL2_25." + sym for sym in SYMBOL_LIST]

endpoint_public = 'wss://stream.bybit.com/realtime_public'

bybit = BybitWS.WebSocket(endpoint_public, subscriptions=BYBIT_DEPTH_NAMES)
binance = socket_master.Binance_SOCK(BINACE_DEPTH_NAMES, isFuture=True)

key_file = open("keys.json")
keys = json.load(key_file)


rest_api = rest_master.Binance_REST(private_key=keys["private"],
                                    public_key=keys["public"])

bybit_rest = BybitREST.HTTP(api_key="k99x1oMaGrpgjmmy6u", api_secret="c9BFkK8GF5QpuAwKrPG7VN7deecXhYhoYyMz")


binance.start()
binance.set_live_and_historic_depth(rest_api)


bidDiff = {}

askDiff = {}

done = False

POSITION_SIZE = 0.01

SECONDS_IN_5_MIN = 5*60
count = 0

trackShort = False
trackLong = False

enterTime = 0
pending = False
orderID = 0

time.sleep(1)

while not done:

    if (pending):
        res = queryOrder(BUSD[0], orderID)
        if res["status"] != "FILLED" and (time.time() - enterTime > 1.5):
            cancelOrder(BUSD[0], orderID)
            trackShort = False
            trackLong = False
            pending = False
            time.sleep(0.2)
        elif res["status"] == "FILLED":
            if (res["side"] == "BUY"):
                trackLong = True
                print("LONG position binance price {}".format(res["avgPrice"]))
            else:
                trackShort = True
                print("SHORT position binance price {}".format(res["avgPrice"]))
            pending = False
        else:
            time.sleep(0.2)
        continue

    depth = binance.get_live_depths(BUSD[0])

    # print(depth)
    # time.sleep(0.2)

    # continue

    bybit_depth = bybit.fetch(BYBIT_DEPTH_NAMES[0])
    minAsk = 200000
    highBid = 0
    for entry in bybit_depth:
        price = float(entry["price"])
        if entry["side"] == "Buy":
            if price > highBid:
                highBid = price
        elif entry["side"] == "Sell":
            if price < minAsk:
                minAsk = price
    
    binanceAsk = depth['a'][0][1]

    percentDiff = ((minAsk - binanceAsk) / binanceAsk ) * 100
    percentDiff = round(percentDiff, 3)
    #print(binanceAsk, minAsk, percentDiff)
    if (percentDiff in askDiff):
        askDiff[percentDiff] += 1
    else:
        askDiff[percentDiff] = 1


    # if (trackShort and percentDiff > -0.04):
    #     res = sendMarketOrder(BUSD[0], "LONG", POSITION_SIZE, rest_api)
    #     trackShort = False
    #     print("Close SHORT binance price {} , bybit price {}".format(binanceAsk, minAsk))

    # if (percentDiff > 0.021 and not trackLong):
    #     res = sendMarketOrder(BUSD[0], "LONG", POSITION_SIZE, rest_api)
    #     orderID = res["clientOrderId"]
    #     pending = True
    #     enterTime=time.time()
    #     print("Opportunity {} {}".format(binanceAsk, minAsk))



    binanceBid = depth['b'][0][1]
    percentDiff = ((highBid - binanceBid) / binanceBid ) * 100
    percentDiff = round(percentDiff, 3)

    if (percentDiff in bidDiff):
        bidDiff[percentDiff] += 1
    else:
        bidDiff[percentDiff] = 1

    # if (percentDiff < -0.12 and not trackShort):
    #     res = sendMarketOrder(BUSD[0], "SHORT", POSITION_SIZE, rest_api)
    #     orderID = res["clientOrderId"]
    #     pending = True
    #     enterTime=time.time()
    #     print("Opportunity {} {}".format(binanceBid, highBid))
        

    # if (trackLong and percentDiff < -0.05):
    #     res = sendMarketOrder(BUSD[0], "SHORT", POSITION_SIZE, rest_api)
    #     trackLong = False
    #     print("Close LONG binance price {} , bybit price {}".format(binanceBid, highBid))


    # count += 1

    # if (count == SECONDS_IN_5_MIN):
    #     count = 0
    #     with open("datacollect.json", "w") as file:
    #         output = {}
    #         output["ask"] = askDiff
    #         output["bid"] = bidDiff
    #         json.dump(output, file)
    # else:
    #     time.sleep(1)
    
    if msvcrt.kbhit():
        print ("you pressed",msvcrt.getch(),"so now i will quit")
        done = True


binance.stop()


# with open("datacollect.json", "w") as file:
#         output = {}
#         output["ask"] = askDiff
#         output["bid"] = bidDiff
#         json.dump(output, file)
