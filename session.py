# modules
from SmartApi.smartConnect import SmartConnect
import pyotp

# credentials
import document_detail as dd

class Session:

    def __init__(self):
        self.smart_api = None
        self.current_session = None


    def session(self):
        _totp = pyotp.TOTP(dd.TOTP)
        _totp = _totp.now()
        self.smart_api = SmartConnect(api_key=dd.API_KEY)
        self.current_session = self.smart_api.generateSession(dd.CLIENT_ID, dd.PASSWORD, totp=_totp)
