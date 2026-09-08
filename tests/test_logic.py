import unittest

from bs4 import BeautifulSoup

from bot import _extract_jsonld_price, _parse_price


class ParsePriceTests(unittest.TestCase):
    def test_parses_currency_and_thousands_separator(self):
        self.assertEqual(_parse_price("$1,299.90"), 1299.90)

    def test_parses_currency_without_decimal(self):
        self.assertEqual(_parse_price("£79"), 79.0)

    def test_returns_none_for_invalid_text(self):
        self.assertIsNone(_parse_price("price unavailable"))

    def test_reads_schema_product_price(self):
        html = '''
        <script type="application/ld+json">
        {"@type":"Product","offers":{"price":"299.00","priceCurrency":"AUD"}}
        </script>
        '''
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(_extract_jsonld_price(soup), 299.00)


if __name__ == "__main__":
    unittest.main()
