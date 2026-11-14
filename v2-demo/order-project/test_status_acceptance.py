import unittest
from order_service import orders_for

class StatusTests(unittest.TestCase):
    def test_no_filter(self):
        self.assertEqual(orders_for(2), [{'id': 11, 'item': 'mouse'}])
    def test_ben_shipped_excludes_ana(self):
        self.assertEqual(orders_for(2, 'shipped'), [{'id': 11, 'item': 'mouse'}])
    def test_ben_pending(self):
        self.assertEqual(orders_for(2, 'pending'), [])
    def test_ana_pending(self):
        self.assertEqual(orders_for(1, 'pending'), [{'id': 10, 'item': 'keyboard'}])
    def test_ana_shipped(self):
        self.assertEqual(orders_for(1, 'shipped'), [{'id': 12, 'item': 'monitor'}])
    def test_invalid_status(self):
        with self.assertRaisesRegex(ValueError, 'unknown status'):
            orders_for(2, 'lost')
    def test_unknown_user(self):
        with self.assertRaisesRegex(ValueError, 'unknown user'):
            orders_for(99, 'shipped')

class ValidationOrderTests(unittest.TestCase):
    def test_unknown_user_precedes_invalid_status(self):
        with self.assertRaisesRegex(ValueError, 'unknown user'):
            orders_for(99, 'lost')

if __name__ == '__main__':
    unittest.main()
