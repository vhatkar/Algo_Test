# modules
# from SmartApi import SmartConnect
from SmartApi.smartConnect import SmartConnect
import pandas as pd
import time
import pyotp
import json

# credentials
import document_detail as dd
from tests.test_candle_data import candle_data


class EMA:
    # Constants
    TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
    EXCHANGE = "NSE"
    SYMBOL_TOKEN = "3045"

    def __init__(self):
        self.smart_api = SmartConnect(api_key=dd.API_KEY)

    def get_historical_data(self, symbol, interval, duration):
        """Fetch historical data to calculate EMA."""

        params = {
            "exchange": self.EXCHANGE,
            "symboltoken": symbol,
            "interval": interval,
            "fromdate": duration[0],  # Start date
            "todate": duration[1]    # End date
        }

        response = self.smart_api.getCandleData(params)
        candle_data = response['data']
        print(json.dumps(candle_data, indent=4))
        print('+++ candle data ', json.dumps(candle_data, indent=4))
        print('+++ is candle data list of list ', candle_data)
        self.smart_api.terminateSession(dd.CLIENT_ID)
        return pd.DataFrame(candle_data, columns=["datetime", "open", "high", "low", "close", "volume"])

    def calculate_ema(self, data, period=21):
        """Calculate the 21 EMA."""
        data['EMA_21'] = data['close'].ewm(span=period, adjust=False).mean()
        return data


# Strategy Execution
def main():
    start_date = "2024-01-01 09:15"
    end_date = "2024-02-01 15:30"
    time_interval = "ONE_DAY"
    ema = EMA()
    totp = pyotp.TOTP(dd.TOTP)
    totp = totp.now()
    session = ema.smart_api.generateSession(dd.CLIENT_ID, dd.PASSWORD, totp=totp)
    token = session['data']['refreshToken']
    print('+++ token ', token)
    ema.smart_api.setAccessToken(token)

    # historical params
    # Fetch historical data for EMA calculation
    data = ema.get_historical_data(ema.SYMBOL_TOKEN, time_interval, [start_date, end_date])
    print('+++ historical data ', data)
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
    #         break

    #     time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

#TODO continue from here
