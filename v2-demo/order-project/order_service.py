"""Small offline teaching project. Caller IDs are fixtures, not authentication."""
USERS = {1: 'Ana', 2: 'Ben'}
ORDERS = [
    {'id': 10, 'user_id': 1, 'item': 'keyboard', 'status': 'pending'},
    {'id': 11, 'user_id': 2, 'item': 'mouse', 'status': 'shipped'},
    {'id': 12, 'user_id': 1, 'item': 'monitor', 'status': 'shipped'},
]


def orders_for(user_id, status=None):
    if user_id not in USERS:
        raise ValueError('unknown user')
    if status is not None and status not in ('pending', 'shipped'):
        raise ValueError('unknown status')
    return [
        {'id': order['id'], 'item': order['item']}
        for order in ORDERS
        if order['user_id'] == user_id
        and (status is None or order['status'] == status)
    ]
