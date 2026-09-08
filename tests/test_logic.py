import unittest

from bot import _parse_price


class ParsePriceTests(unittest.TestCase):
    def test_parses_currency_and_thousands_separator(self):
        self.assertEqual(_parse_price("$1,299.90"), 1299.90)

    def test_parses_currency_without_decimal(self):
        self.assertEqual(_parse_price("£79"), 79.0)

    def test_returns_none_for_invalid_text(self):
        self.assertIsNone(_parse_price("price unavailable"))


if __name__ == "__main__":
    unittest.main()
