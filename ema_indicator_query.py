# modules
from SmartApi.smartConnect import SmartConnect
import pandas as pd
import pyotp
import json

# credentials
import document_detail as dd


class EMA:
    # Constants
    TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
    EXCHANGE = "NSE"
    SYMBOL_TOKEN = "3045"

    def __init__(self):
        _totp = pyotp.TOTP(dd.TOTP)
        _totp = _totp.now()
        self.smart_api = SmartConnect(api_key=dd.API_KEY)
        self.session = self.smart_api.generateSession(dd.CLIENT_ID, dd.PASSWORD, totp=_totp)

    def get_historical_data(self, symbol, interval, duration):
        """Fetch historical data to calculate EMA."""

        historicDataParams = {
            "exchange": self.EXCHANGE,
            "symboltoken": symbol,
            "interval": interval,
            "fromdate": duration[0],  # Start date
            "todate": duration[1]    # End date
        }

        response = self.smart_api.getCandleData(historicDataParams)
        _candle_data = response['data']
        self.smart_api.terminateSession(dd.CLIENT_ID)
        return pd.DataFrame(_candle_data, columns=["datetime", "open", "high", "low", "close", "volume"])

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
    # token = session['data']['refreshToken']
    # print('+++ token ', token)
    # ema.smart_api.setAccessToken(token)

    # historical params
    # Fetch historical data for EMA calculation
    try:
        _historical_data = ema.get_historical_data(ema.SYMBOL_TOKEN, time_interval, [start_date, end_date])
        _ema_data = ema.calculate_ema(_historical_data)
        print('+++ _ema data ', _ema_data)
        print("ONE DAY \n", _ema_data.to_markdown())
        last_row = _ema_data.iloc[-1]
        if last_row['close'] > last_row['EMA_21']:
            print("Condition met. Placing order because last close is greater than last ema_21 ")
    except Exception as e:
        print(f"Error fetching candle data: {str(e)}")

if __name__ == "__main__":
    main()
