import unittest
from tests.api_live import add_numbers  # Example function

class TestModule1(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(add_numbers(2, 3), 5)

if __name__ == "__main__":
    unittest.main()
