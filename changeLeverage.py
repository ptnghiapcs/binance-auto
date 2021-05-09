from binance_api import rest_master
import time
import json

rest_api = rest_master.Binance_REST(private_key="M3rVcyKwP1xNhQRTHJy1I6RmHqK4OHwFnbtGYsW18F4IorXavoSWCpGa3JmV3KNh",
                                    public_key="8fKELP10OY69D8Sq47DjnQv9GHrjjpgRsVXDt9p15O5k36r06aEGZfKinxKbv1ls")
            
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