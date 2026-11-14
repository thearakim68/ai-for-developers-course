"""Command-line interface for the offline order service.

Owner identifiers are fictional fixtures, not authentication.
Uses only the Python standard library. No provider or network calls.
"""

import argparse
import json
import sys

from order_service import orders_for


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List orders for a fictional fixture user.",
    )
    parser.add_argument("--user", required=True, type=int, help="fixture user id")
    parser.add_argument(
        "--status", default=None, help="order status filter (pending or shipped)"
    )
    args = parser.parse_args(argv)

    try:
        result = orders_for(args.user, args.status)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())