
from urllib.parse import urlencode
from binance_api import socket_master, rest_master
import time

rest_api = rest_master.Binance_REST(private_key="M3rVcyKwP1xNhQRTHJy1I6RmHqK4OHwFnbtGYsW18F4IorXavoSWCpGa3JmV3KNh",
                                    public_key="8fKELP10OY69D8Sq47DjnQv9GHrjjpgRsVXDt9p15O5k36r06aEGZfKinxKbv1ls")
            

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

def openPosition(symbol, side, amount, price):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount
    order["price"] = price
    order["timeInForce"] = "GTC"
    if (side == "LONG"):
        order["side"] = "BUY"
    else:
        order["side"] = "SELL"
    order["type"] = "LIMIT"
    currMili = round(time.time() * 1000)
    order["timestamp"] = currMili
    return order


def sendOrder(symbol, side, amount, price, rest_api, sl=None, tp=None, ):
    openPos = openPosition(symbol, side, amount, price)
    rest_api.api_request("POST", "/fapi/v1/order", openPos, True, True, 'https://fapi.binance.com')

    if (sl is not None):
        slOrder = createSL(symbol,side,amount,sl)
        rest_api.api_request("POST", "/fapi/v1/order", slOrder, True, True, 'https://fapi.binance.com')

    if (tp is not None):
        tpOrder = createTP(symbol, side, amount,tp)
        rest_api.api_request("POST", "/fapi/v1/order", tpOrder, True, True, 'https://fapi.binance.com')



# orders = []
# tp = createTP("EOSUSDT", "LONG", 1.5, 11)
# sl = createSL("EOSUSDT", "LONG", 1.5, 10)
# op = openPosition("EOSUSDT", "LONG", 1.5, 10.53)
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