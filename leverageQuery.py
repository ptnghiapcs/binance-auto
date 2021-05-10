from binance_api import rest_master
import time
import json

rest_api = rest_master.Binance_REST(private_key="M3rVcyKwP1xNhQRTHJy1I6RmHqK4OHwFnbtGYsW18F4IorXavoSWCpGa3JmV3KNh",
                                    public_key="8fKELP10OY69D8Sq47DjnQv9GHrjjpgRsVXDt9p15O5k36r06aEGZfKinxKbv1ls")
            

currMili = round(time.time() * 1000)

result = rest_api.get_leverage_brackets(timestamp=currMili)


exchanage_info = rest_api.api_request("GET", "/fapi/v1/exchangeInfo", {}, False, False, 'https://fapi.binance.com')

temp = {}
tickSize = {}

for symbol in exchanage_info["symbols"]:
    temp[symbol["symbol"]] = float(symbol["filters"][1]["stepSize"])
    tickSize[symbol["symbol"]] = float(symbol["filters"][0]["tickSize"])

savedSymbol = []
file = open("symbols.json", "w")

offset = 0

for i, symbolInfo in enumerate(result):
    if ("_" in symbolInfo["symbol"] or "DOTECOUSDT" == symbolInfo["symbol"] or "DEFIUSDT" == symbolInfo["symbol"] or "LENDUSDT" == symbolInfo["symbol"] or "BTCSTUSDT" == symbolInfo["symbol"] or ("USDT" not in symbolInfo["symbol"])):
        offset+=1
        continue
    symbol = {}
    symbol["symbol"] = symbolInfo["symbol"]
    symbol["leverage"] = symbolInfo["brackets"][0]["initialLeverage"]
    symbol["stepSize"] = temp[symbol["symbol"]]
    symbol["tickSize"] = tickSize[symbol["symbol"]]
    savedSymbol.append(symbol)
    print("Symbol: {}, Leverage: {}, MaxNotion: {}".format(symbolInfo["symbol"], symbolInfo["brackets"][0]["initialLeverage"], symbolInfo["brackets"][0]["notionalCap"]))

print(len(savedSymbol))

json.dump(savedSymbol, file)

