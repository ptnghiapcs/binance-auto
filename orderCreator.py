def createTP(symbol, side, amount, time, tp):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount

    if (side == "LONG"):
        order["side"] = "SELL"
    else:
        order["side"] = "BUY"
    order["TYPE"] = "TAKE_PROFIT_MARKET"
    order["reduceOnly"] = "true"
    order["timestamp"] = time
    order["stopPrice"] = tp
    return order

def createSL(symbol, side, amount, time, sl):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount
    if (side == "LONG"):
        order["side"] = "SELL"
    else:
        order["side"] = "BUY"
    order["TYPE"] = "STOP_MARKET"
    order["reduceOnly"] = "true"
    order["timestamp"] = time
    order["stopPrice"] = sl
    return order

def openPosition(symbol, side, amount, time, price):
    order={}
    order["symbol"] = symbol
    order["quantity"] = amount
    order["price"] = price
    order["timeInForce"] = "GTC"
    if (side == "LONG"):
        order["side"] = "SELL"
    else:
        order["side"] = "BUY"
    order["TYPE"] = "LIMIT"
    order["timestamp"] = time
    return order


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