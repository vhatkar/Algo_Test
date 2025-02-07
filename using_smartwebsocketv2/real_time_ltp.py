import auto_authenticate

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

correlation_id = "ws_test"
action = 1  # action = 1, subscribe to the feeds action = 2 - unsubscribe
mode = 1  # mode = 1 , Fetches LTP quotes

token_list = [
    {
        "exchangeType": 2,
        "tokens": ["57920", "57919"]
    }
]
token_list1 = [
    {
        "exchangeType": 1,
        "tokens": ["26000", "26009"]
    }
]

sws = SmartWebSocketV2(AUTH_TOKEN, apikey, username, FEED_TOKEN, max_retry_attempt=5)


# row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price}"


def on_data(wsapp, message):
    # Convert timestamp from milliseconds to seconds
    timestamp = message['exchange_timestamp'] / 1000  # Convert to seconds
    utc_time = datetime.utcfromtimestamp(timestamp)

    # Define the timezone for UTC +05:30
    timezone = pytz.timezone('Asia/Kolkata')  # 'Asia/Kolkata' is the timezone for UTC +05:30

    # Convert UTC time to UTC +05:30
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')

    # Define the format for the output with two decimal places for Last Traded Price
    row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price:.2f}, Timestamp: {timestamp}"

    # Format the message data
    formatted_row = row_format.format(
        exchange_type=message['exchange_type'],
        token=message['token'],
        last_traded_price=message['last_traded_price'] / 100,
        # Assuming this division by 100 is required for your specific case
        timestamp=formatted_timestamp
    )

    # Print the formatted data
    logger.info(formatted_row)


def on_open(wsapp):
    logger.info("on open")
    sws.subscribe(correlation_id, mode, token_list)
    sws.subscribe(correlation_id, mode, token_list1)

    # sws.unsubscribe(correlation_id, mode, token_list1)


def on_error(wsapp, error):
    logger.info(error)


def on_close(wsapp):
    logger.info("Close")


def close_connection():
    sws.close_connection()


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

threading.Thread(target=sws.connect).start()

