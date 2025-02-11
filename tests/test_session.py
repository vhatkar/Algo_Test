import unittest
from session import Session  # Import the class to be tested

class TestSession(unittest.TestCase):

    def setUp(self):
        """Runs before each test"""
        self.sess = Session()

    def test_smart_api(self):
        self.assertIsNotNone(self.sess.smart_api)

    def test_login_response(self):
        self.assertIsNotNone(self.sess.login_response)

    def test_auth_token(self):
        self.assertIsNotNone(self.sess.auth_token())

    def test_refresh_token(self):
        self.assertIsNotNone(self.sess.refresh_token())

    def test_feed_token(self):
        self.assertIsNotNone(self.sess.feed_token())


if __name__ == '__main__':
    unittest.main()
