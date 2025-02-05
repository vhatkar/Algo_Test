# modules
from SmartApi.smartConnect import SmartConnect
import pyotp

# credentials
import document_detail as dd

class Session:

    def __init__(self):
        self.session()

    def session(self):
        _totp = pyotp.TOTP(dd.TOTP)
        _totp = _totp.now()
        self.smart_api = SmartConnect(api_key=dd.API_KEY) or None
        self.current_session = self.smart_api.generateSession(dd.CLIENT_ID, dd.PASSWORD, totp=_totp) or None
