from binance_api import rest_master
import time
import json

rest_api = rest_master.Binance_REST(private_key="M3rVcyKwP1xNhQRTHJy1I6RmHqK4OHwFnbtGYsW18F4IorXavoSWCpGa3JmV3KNh",
                                    public_key="8fKELP10OY69D8Sq47DjnQv9GHrjjpgRsVXDt9p15O5k36r06aEGZfKinxKbv1ls")
            

currMili = round(time.time() * 1000)

result = rest_api.get_leverage_brackets(timestamp=currMili)


savedSymbol = []
file = open("symbols.json", "w")

for symbolInfo in result:
    if ("_" in symbolInfo["symbol"] or "DOTECOUSDT" == symbolInfo["symbol"] or "DEFIUSDT" == symbolInfo["symbol"]):
        continue
    symbol = {}
    symbol["symbol"] = symbolInfo["symbol"]
    symbol["leverage"] = symbolInfo["brackets"][0]["initialLeverage"]
    savedSymbol.append(symbol)
    print("Symbol: {}, Leverage: {}, MaxNotion: {}".format(symbolInfo["symbol"], symbolInfo["brackets"][0]["initialLeverage"], symbolInfo["brackets"][0]["notionalCap"]))

print(len(savedSymbol))

json.dump(savedSymbol, file)