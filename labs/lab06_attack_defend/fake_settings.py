"""Lab 6 practice file. The key below is FAKE and does nothing.

It looks like a real API key on purpose, so you can practise catching it
with gitleaks before it is committed. In real code, keys live in .env
(which is git-ignored) and are read with os.environ.
"""

PAYMENT_API_URL = "https://payments.example.invalid/v1"
PAYMENT_API_KEY = "sk-demo-NOT-A-REAL-KEY-0000"  # <- gitleaks should flag this line
