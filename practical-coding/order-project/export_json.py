import json
from order_service import orders_for
original = orders_for(2, 'shipped')
text = json.dumps(original)
print(text)
assert json.loads(text) == original
print('Round trip passed')
