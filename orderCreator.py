
from urllib.parse import urlencode
from binance_api import socket_master, rest_master
import time

key_file = open("keys.json")
keys = json.load(key_file)


rest_api = rest_master.Binance_REST(private_key=keys["private"],
                                    public_key=keys["public"])
            

BASE_ORDER = {}
BASE_ORDER["symbol"] = "A"
BASE_ORDER["quantity"] = 1
BASE_ORDER["price"] = 0.1
BASE_ORDER["timeInForce"] = "GTX"
BASE_ORDER["side"] = "BUY"
BASE_ORDER["type"] = "LIMIT"
BASE_ORDER["timestamp"] = 1
BASE_ORDER["newOrderRespType"] = "RESULT"


BASE_MARKET_ORDER = {}
BASE_MARKET_ORDER["symbol"] = "A"
BASE_MARKET_ORDER["quantity"] = 1
BASE_MARKET_ORDER["side"] = "BUY"
BASE_MARKET_ORDER["type"] = "MARKET"
BASE_MARKET_ORDER["timestamp"] = 1
BASE_MARKET_ORDER["newOrderRespType"] = "RESULT"

def createTP(symbol, side, amount, tp):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount

    if (side == "LONG"):
        order["side"] = "SELL"
    else:
        order["side"] = "BUY"
    order["type"] = "TAKE_PROFIT_MARKET"
    order["reduceOnly"] = "true"
    order["stopPrice"] = tp
    order["workingType"] = "MARK_PRICE"
    currMili = round(time.time() * 1000)
    order["timestamp"] = currMili
    return order

def createSL(symbol, side, amount, sl):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount
    if (side == "LONG"):
        order["side"] = "SELL"
    else:
        order["side"] = "BUY"
    order["type"] = "STOP_MARKET"
    order["reduceOnly"] = "true"
    order["stopPrice"] = sl
    order["workingType"] = "MARK_PRICE"
    currMili = round(time.time() * 1000)
    order["timestamp"] = currMili
    return order

def openLimitPosition(symbol, side, amount, price):
    BASE_ORDER["symbol"] = symbol
    BASE_ORDER["quantity"] = amount
    BASE_ORDER["price"] = price
    if (side == "LONG"):
        BASE_ORDER["side"] = "BUY"
    else:
        BASE_ORDER["side"] = "SELL"
    BASE_ORDER["timestamp"] = round(time.time() * 1000)
    return BASE_ORDER

def openMarketPosition(symbol, side, amount):
    BASE_MARKET_ORDER["symbol"] = symbol
    BASE_MARKET_ORDER["quantity"] = amount
    if (side == "LONG"):
        BASE_MARKET_ORDER["side"] = "BUY"
    else:
        BASE_MARKET_ORDER["side"] = "SELL"
    BASE_MARKET_ORDER["timestamp"] = round(time.time() * 1000)
    return BASE_MARKET_ORDER



def sendOrder(symbol, side, amount, price, rest_api, sl=None, tp=None):
    openPos = openLimitPosition(symbol, side, amount, price)
    res = rest_api.api_request("POST", "/fapi/v1/order", openPos, True, True, 'https://fapi.binance.com')

    if (sl is not None):
        slOrder = createSL(symbol,side,amount,sl)
        rest_api.api_request("POST", "/fapi/v1/order", slOrder, True, True, 'https://fapi.binance.com')

    if (tp is not None):
        tpOrder = createTP(symbol, side, amount,tp)
        rest_api.api_request("POST", "/fapi/v1/order", tpOrder, True, True, 'https://fapi.binance.com')

    return res

def sendMarketOrder(symbol, side, amount, rest_api):
    openPos = openMarketPosition(symbol, side, amount)
    res = rest_api.api_request("POST", "/fapi/v1/order", openPos, True, True, 'https://fapi.binance.com')
    return res

def cancelOrder(symbol, id):
    data = {}
    data["symbol"] =symbol
    data["origClientOrderId"] = id
    data["timestamp"]= round(time.time() * 1000)

    res = rest_api.api_request("DELETE", "/fapi/v1/order", data, True, True, 'https://fapi.binance.com')
def queryOrder(symbol, id):
    data = {}
    data["symbol"] =symbol
    data["origClientOrderId"] = id
    data["timestamp"]= round(time.time() * 1000)
        
    return rest_api.api_request("GET", "/fapi/v1/order", data, True, True, 'https://fapi.binance.com')

# orders = []
# tp = createTP("EOSUSDT", "LONG", 1.5, 11)
# sl = createSL("EOSUSDT", "LONG", 1.5, 10)
# op = oLimit
#penPosition("EOSUSDT", "LONG", 1.5, 10.53)
# orders.append(tp)
# orders.append(sl)
# orders.append(op)   



# params = {}
# params["batchOrders"] = orders
# # print(urlencode(sorted(params.items())))


# currMili = round(time.time() * 1000)
# params["timestamp"] = currMili
# print(rest_api.api_request("POST", "/fapi/v1/batchOrders", params, True, True, 'https://fapi.binance.com'))


# res = rest_api.send_batchOrder(batchOrders=orders, timestamp=currMili)
    # print(res)


# symbol 	STRING 	YES 	
# side 	    ENUM 	YES 	
# positionSide 	ENUM 	NO
# type 	ENUM 	YES 	
# timeInForce 	ENUM 	NO 	
# quantity 	DECIMAL 	NO
# reduceOnly 	STRING 	NO
# price 	DECIMAL 	NO 	
# newClientOrderId 	STRING 	NO
# stopPrice 	DECIMAL 	NO
# closePosition 	STRING 	NO
# activationPrice 	DECIMAL 	NO
# callbackRate 	DECIMAL 	NO
# workingType 	ENUM 	NO
# priceProtect 	STRING 	NO
# newOrderRespType 	ENUM 	NO
# recvWindow 	LONG 	NO 	
# timestamp 	LONG 	YES