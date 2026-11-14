import copy
import unittest
from unittest.mock import patch

from order_service import orders_for


class AIBoundaryTests(unittest.TestCase):

    def test_shipped_orders_preserve_source_order_and_exclude_other_owners_and_pending(self):
        """Unsorted integer IDs, interleaved owners/statuses, two shipped for Ben.

        Detects: ownership leak when status is supplied (status-only filter),
        status filter failing to exclude pending orders, and result-order
        not matching ORDERS source order.
        """
        fixture = [
            {'id': 100, 'user_id': 2, 'item': 'mouse', 'status': 'shipped'},
            {'id': 50, 'user_id': 1, 'item': 'keyboard', 'status': 'pending'},
            {'id': 25, 'user_id': 2, 'item': 'headset', 'status': 'shipped'},
            {'id': 75, 'user_id': 1, 'item': 'monitor', 'status': 'shipped'},
            {'id': 10, 'user_id': 2, 'item': 'keyboard', 'status': 'pending'},
        ]
        expected = [
            {'id': 100, 'item': 'mouse'},
            {'id': 25, 'item': 'headset'},
        ]
        with patch('order_service.ORDERS', fixture):
            result = orders_for(2, 'shipped')
        self.assertEqual(result, expected)

    def test_orders_for_does_not_mutate_fixture_list_or_dictionaries(self):
        """Unsorted integer IDs; calls with and without status leave ORDERS intact.

        Detects: in-place mutation of ORDERS (append/sort/filter) or of its
        order dictionaries (adding/changing keys), across both filtered and
        unfiltered calls.
        """
        fixture = [
            {'id': 100, 'user_id': 1, 'item': 'keyboard', 'status': 'pending'},
            {'id': 10, 'user_id': 2, 'item': 'mouse', 'status': 'shipped'},
            {'id': 50, 'user_id': 1, 'item': 'monitor', 'status': 'shipped'},
        ]
        snapshot = copy.deepcopy(fixture)
        with patch('order_service.ORDERS', fixture):
            orders_for(2, 'shipped')
            orders_for(2)
        self.assertEqual(fixture, snapshot)


if __name__ == '__main__':
    unittest.main()
