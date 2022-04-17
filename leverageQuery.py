from binance_api import rest_master
import time
import json

key_file = open("keys.json")
keys = json.load(key_file)


rest_api = rest_master.Binance_REST(private_key=keys["private"],
                                    public_key=keys["public"])
            

currMili = round(time.time() * 1000)

result = rest_api.get_leverage_brackets(timestamp=currMili)


exchanage_info = rest_api.api_request("GET", "/fapi/v1/exchangeInfo", {}, False, False, 'https://fapi.binance.com')

temp = {}
tickSize = {}

for symbol in exchanage_info["symbols"]:
    one = symbol["filters"][1]["stepSize"].find('1')
    temp[symbol["symbol"]] = symbol["filters"][1]["stepSize"][:(one + 1)]
    one = symbol["filters"][0]["tickSize"].find('1')
    tickSize[symbol["symbol"]] = symbol["filters"][0]["tickSize"][:(one+1)]

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

