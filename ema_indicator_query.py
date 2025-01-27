# modules
from smartapi import SmartConnect
import pandas as pd
import time


# credentials
import document_detail as dd


# Constants
TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
EXCHANGE = "NSE"
SYMBOL_TOKEN = "3045"

def get_historical_data(symbol, interval, duration):
    """Fetch historical data to calculate EMA."""

    params = {
        "exchange": EXCHANGE,
        "symboltoken": symbol,
        "interval": interval,
        "fromdate": duration[0],  # Start date
        "todate": duration[1]    # End date
    }
    response = obj.getCandleData(params)
    obj.terminateSession(dd.USER_ID)
    return pd.DataFrame(response['data'], columns=["datetime", "open", "high", "low", "close", "volume"])


def calculate_ema(data, period=21):
    """Calculate the 21 EMA."""
    data['EMA_21'] = data['close'].ewm(span=period, adjust=False).mean()
    return data


def place_order(symbol, qty):
    """Place a buy order for the future."""
    obj = SmartConnect(api_key=dd.API_KEY)
    obj.generateSession(dd.USER_ID, dd.PASSWORD)
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": SYMBOL_TOKEN,  # Get token dynamically
        "transactiontype": "BUY",
        "exchange": EXCHANGE,
        "ordertype": "MARKET",
        "quantity": qty,
        "producttype": "INTRADAY"
    }
    order_id = obj.placeOrder(order_params)
    print(f"Order placed successfully. ID: {order_id}")

# Strategy Execution
def main():
    start_date = "2025-01-01 09:15"
    end_date = "2025-01-27 15:30"
    time_interval = "15min"
    # Fetch historical data for EMA calculation
    data = get_historical_data(TRADING_SYMBOL, time_interval, [start_date, end_date])
    # data = calculate_ema(data)

    # # Monitor live data
    # while True:
    #     # Fetch latest data (pseudo-code, replace with live WebSocket fetch)
    #     latest_data = get_historical_data(TRADING_SYMBOL, time_interval, [start_date, end_date])
    #     latest_data = calculate_ema(latest_data)

    #     # Check if the closing price is above EMA
    #     last_row = latest_data.iloc[-1]
    #     if last_row['close'] > last_row['EMA_21']:
    #         print("Condition met. Placing order.")
    #         place_order(TRADING_SYMBOL, qty=1)
    #         break

    #     time.sleep(60)  # Check every minute

if _name_ == "_main_":
    obj = SmartConnect(api_key=dd.API_KEY)
    data = obj.generateSession(dd.USER_ID, dd.PASSWORD)
    token = data['data']['refreshToken']
    obj.setAccessToken(token)

    main()
