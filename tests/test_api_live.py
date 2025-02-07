import websocket
import json
import threading
import document_detail as dd

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

# WebSocket Client (Subject)
class WebSocketClient:
    YOUR_ACCESS_TOKEN = dd.TOTP
    SYMBOL_TOKEN = "3045"
    TRADING_SYMBOL = "SBIN-EQ"
    EXCHANGE = "NSE"

    def __init__(self, url):
        self.url = url
        self.observers = []
        self.ws = None

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def on_message(self, ws, message):
        print("[WebSocket] Message received")
        self.notify_observers(message)

    def on_error(self, ws, error):
        print("[WebSocket] Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("[WebSocket] Connection closed")

    def on_open(self, ws):
        print("[WebSocket] Connection opened")
        subscribe_payload = {
            "action": "subscribe",
            "token": self.YOUR_ACCESS_TOKEN,
            "feedtype": "ltp",
            "segment": self.EXCHANGE,
            "symbol": self.TRADING_SYMBOL
        }
        ws.send(json.dumps(subscribe_payload))
        print("[WebSocket] Subscription sent")

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open

        # Run WebSocket in a separate thread to keep the main thread free
        thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        thread.start()

# Instantiate the WebSocket client
ws_client = WebSocketClient("wss://wsapi.angelbroking.com/live")

# Attach observers
logger = LoggerObserver()
alert = AlertObserver()
ws_client.add_observer(logger)
ws_client.add_observer(alert)

# Start the WebSocket connection
ws_client.start()

# Keep the main thread alive
while True:
    pass  # You can replace this with an event loop or application logic
