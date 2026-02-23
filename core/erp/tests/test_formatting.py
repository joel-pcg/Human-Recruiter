from decimal import Decimal

from core.erp.formatting import format_as_dominican_currency


class TestFormatAsDominicanCurrency:
    def test_integer_value(self):
        assert format_as_dominican_currency(1000) == '1,000.00'

    def test_decimal_value(self):
        assert format_as_dominican_currency(Decimal('25000.50')) == '25,000.50'

    def test_zero(self):
        assert format_as_dominican_currency(0) == '0.00'

    def test_large_value(self):
        assert format_as_dominican_currency(Decimal('1234567.89')) == '1,234,567.89'

    def test_small_value(self):
        assert format_as_dominican_currency(Decimal('0.99')) == '0.99'
