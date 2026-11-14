import unittest
from order_service import orders_for


class OrderTests(unittest.TestCase):
    def test_ana_gets_only_her_orders(self):
        self.assertEqual(orders_for(1), [
            {'id': 10, 'item': 'keyboard'},
            {'id': 12, 'item': 'monitor'},
        ])

    def test_ben_gets_only_his_order(self):
        self.assertEqual(orders_for(2), [{'id': 11, 'item': 'mouse'}])

    def test_unknown_caller_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown user'):
            orders_for(99)

    def test_caller_cannot_choose_another_users_order(self):
        self.assertNotIn(10, [order['id'] for order in orders_for(2)])


if __name__ == '__main__':
    unittest.main()
