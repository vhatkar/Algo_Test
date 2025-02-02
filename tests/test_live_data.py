import json
import websocket
from ema_indicator_query import EMA

# Replace with your SmartAPI access token from the session
# token = session['data']['refreshToken']
ema = EMA()
ema.session()
access_token = "your_access_token"

def on_message(ws, message):
    # Handle live data messages here (e.g., live price)
    print("Live Data:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    # Sending subscription request for live market data
    subscribe_data = {
        "symbol": "NSE:RELIANCE",
        "exchange": "NSE",  # Change to the exchange you need data for (e.g., NSE, BSE)
        "token": access_token
    }
    ws.send(json.dumps(subscribe_data))

websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://wsapi.angelbroking.com/live",  # Example WebSocket URL
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
