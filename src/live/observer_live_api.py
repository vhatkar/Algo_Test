##########################################################
# requirements
# AUTH_TOKEN from session
# API_KEY from cnf,
# CLIENT_ID from cnf
# FEED_TOKEN from session
##########################################################

# system modules
import json
import pytz
import time
import datetime
import threading
import pandas as pd
from logzero import logger
from collections import deque
import plotly.graph_objects as go
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from src import config as cnf
from src.session import Session


# instance of session
sess = Session() # get smart_api
AUTH_TOKEN = sess.auth_token()
FEED_TOKEN = sess.feed_token()


# Observer Interface
class WebSocketObserver:
    def update(self, message):
        raise NotImplementedError("Observer must implement the update method.")


# Concrete Observer: Logs messages
class LoggerObserver(WebSocketObserver):
    def update(self, message):
        print("[Logger] Received:", message)


# Concrete Observer: Alerts on a certain condition
class AlertObserver(WebSocketObserver):
    def update(self, message):
        data = json.loads(message)
        print('+++ data ', data)
        # if "price" in data and data["price"] > 1000:  # Example condition
        #     print("[Alert] Price exceeded 1000:", data["price"])


class SmartWebSocketV2Client:
    ACTION = "subscribe"
    FEED_TYPE = "ltp"
    YOUR_ACCESS_TOKEN = cnf.TOTP
    SYMBOL_TOKEN = "3045" # used to get historical data
    TRADING_SYMBOL = "SBIN-EQ"
    EXCHANGE = "NSE"
    # variables
    correlation_id = "ws_test"
    action = 1  # action = 1, subscribe to the feeds action = 2 - unsubscribe
    mode = 1  # mode = 1 , Fetches LTP quotes
    # Tokens to subscribe (Example: Nifty 50)
    token_list = [
        {
            "exchangeType": 2,  # NSE
            "tokens": ["26000"]  # NIFTY 50 Token
        }
    ]
    # Store live data
    data_queue = deque(maxlen=50)  # Store the last 50 data points

    def __init__(self):
        self.observers = []
        self.sws = None

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def time_stamp(self, wsapp, message):
        # Convert timestamp from milliseconds to seconds
        timestamp = message['exchange_timestamp'] / 1000  # Convert to seconds
        utc_time = datetime.utcfromtimestamp(timestamp)

        # Define the timezone for UTC +05:30
        timezone = pytz.timezone('Asia/Kolkata')  # 'Asia/Kolkata' is the timezone for UTC +05:30

        # Convert UTC time to UTC +05:30
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_timestamp

    def on_data(self, wsapp, message):
        """Handles incoming live market data."""

        try:
            formatted_timestamp = self.time_stamp(message)
            data = json.loads(message)
            print('+++ data ', data)
            for item in data["data"]:
                _token = item["token"]
                _item_price = item.get("ltp", 0)  # Last traded price
                row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price:.2f}, Timestamp: {timestamp}"

                # Format the message data
                formatted_row = row_format.format(
                    exchange_type=data['exchange_type'],
                    token=_token,
                    last_traded_price=_item_price / 100,
                    # Assuming this division by 100 is required for your specific case
                    timestamp=formatted_timestamp
                )

                # Store data
                self.data_queue.append(formatted_row)

                # Print latest price
                print(f"Token: {_token}, LTP: {_item_price}")

        except Exception as e:
            print(f"Error processing data: {e}")

    def on_open(self, wsapp):
        """Handles WebSocket opening and subscription."""
        logger.info("on open")
        wsapp.subscribe(self.correlation_id, self.mode, self.token_list)
        # sws.subscribe(correlation_id, mode, self.token_list1)

    def on_close(self, wsapp):
        """Handles WebSocket closing."""
        logger.info("WebSocket Closed!")
        wsapp.close_connection()

    def on_error(self, wsapp, error):
        """Handles WebSocket errors."""
        logger.error(f"Error: {error}")
        # wsapp.unsubscribe(correlation_id, mode, self.token_list)

    def on_message(self, wsapp, message):
        print("[WebSocket] Message received")
        self.notify_observers(message)

    def start(self):

        self.sws = SmartWebSocketV2(
            self.auth_token,
            self.api_key,
            self.client_id,
            self.feed_token,
            max_retry_attempt=5
        )

        self.sws.on_data = self.on_data
        self.sws.on_open = self.on_open
        self.sws.on_close = self.on_close
        self.sws.on_error = self.on_error
        # Run WebSocket in a separate thread to keep the main thread free
        thread = threading.Thread(target=self.sws.run_forever, daemon=True)
        # or
        thread = threading.Thread(target=self.sws.connect)
        thread.start()

    def get_latest_close_greater_than_ema(self, _live_data, time_interval, start_date, end_date):
        # _flag = None
        # try:
        _ema_data = self.calculate_ema(_live_data)
        _ema_sorted = _ema_data.sort_values(by='EMA_21', ascending=True)
        print('+++ ema sorted \n\n', _ema_sorted)
        _greater_than = _ema_sorted[_ema_sorted['close'] > _ema_sorted['EMA_21']]
        print('+++ all greater than \n\n', _greater_than)
        last_row = _ema_sorted.iloc[-1]
        if last_row['close'] > last_row['EMA_21']:
            print("Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                last_row['close'], last_row['EMA_21']))

        _greater_last_row = _greater_than.iloc[-1]
        if _greater_last_row['close'] > _greater_last_row['EMA_21']:
            print("_greater_last_row : Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                _greater_last_row['close'], _greater_last_row['EMA_21']))

        # except Exception as e:
        #     print(f"Error fetching candle data: {str(e)}")
        # return _flag

    def live_chart(self):
        """Updates the chart in real-time."""
        fig = go.Figure()

        while True:
            if len(self.data_queue) > 0:
                df = pd.DataFrame(list(self.data_queue))

                fig.data = []  # Clear old data
                fig.add_trace(go.Scatter(x=df["timestamp"], y=df["last_traded_price"], mode="lines", name="LTP"))
                fig.update_layout(title="Live Market Price", xaxis_title="Time", yaxis_title="Price")
                fig.show()

            time.sleep(2)  # Update every 2 seconds

#
# #sws.connect()
# # or
# swsc = SmartWebSocketV2Client()
# swsc.start()
# # Run the live chart function
# swsc.live_chart()
