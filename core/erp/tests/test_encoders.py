import json
from datetime import date, datetime
from decimal import Decimal

from core.erp.encoders import CustomJSONEncoder


class TestCustomJSONEncoder:
    def test_decimal_encoding(self):
        data = {'amount': Decimal('1234.56')}
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['amount'] == 1234.56

    def test_date_encoding(self):
        data = {'date': date(2024, 1, 15)}
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['date'] == '2024-01-15'

    def test_datetime_encoding(self):
        data = {'dt': datetime(2024, 1, 15, 10, 30, 0)}
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['dt'] == '2024-01-15'

    def test_mixed_types(self):
        data = {
            'amount': Decimal('500.00'),
            'date': date(2024, 6, 1),
            'name': 'Test',
            'count': 42,
        }
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['amount'] == 500.0
        assert result['date'] == '2024-06-01'
        assert result['name'] == 'Test'
        assert result['count'] == 42

    def test_nested_structures(self):
        data = {
            'items': [
                {'price': Decimal('10.50'), 'date': date(2024, 3, 1)},
                {'price': Decimal('20.75'), 'date': date(2024, 3, 2)},
            ]
        }
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['items'][0]['price'] == 10.5
        assert result['items'][1]['date'] == '2024-03-02'
