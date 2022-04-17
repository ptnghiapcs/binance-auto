from binance_api import rest_master
import time
import json

key_file = open("keys.json")
keys = json.load(key_file)


rest_api = rest_master.Binance_REST(private_key=keys["private"],
                                    public_key=keys["public"])
            
try:
    symbolFile = open("symbols.json", "r")
except IOError:
    print("symbols.json NOT FOUND")
    quit()

loadedSymbols = json.load(symbolFile)


for symbol in loadedSymbols:
    currMili = round(time.time() * 1000)
    rest_api.change_leverage(symbol=symbol["symbol"],leverage=symbol["leverage"],timestamp=currMili)
    print("Finish symbol {}".format(symbol["symbol"]))
    time.sleep(0.1)