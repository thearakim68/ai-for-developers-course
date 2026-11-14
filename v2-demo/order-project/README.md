# Order CLI

Offline command-line interface for the fictional order service. Owner
identifiers are fixtures, not authentication. Uses only the Python
standard library. No network or provider calls.

## Setup

Run from the project directory:

```
python orders_cli.py --user <id> [--status <status>]
```

## Arguments

- `--user` (required, integer): fixture user id (`1` = Ana, `2` = Ben).
- `--status` (optional): order status filter, either `pending` or `shipped`.

## Examples

Ben, shipped orders:

```
python orders_cli.py --user 2 --status shipped
```
Exit 0. stdout: `[{"id": 11, "item": "mouse"}]`

Ana, no status filter:

```
python orders_cli.py --user 1
```
Exit 0. stdout: `[{"id": 10, "item": "keyboard"}, {"id": 12, "item": "monitor"}]`

Ben, pending orders:

```
python orders_cli.py --user 2 --status pending
```
Exit 0. stdout: `[]`

Unknown user:

```
python orders_cli.py --user 99 --status lost
```
Exit 2. Empty stdout. stderr: `error: unknown user`

## Behavior

- Success: exit 0, one JSON list on stdout containing only `id` and `item`,
  preserving source order. Source data is not mutated.
- Service `ValueError` (unknown user or unknown status): exit 2, empty
  stdout, stderr `error: <message>`. User is validated before status.
- Missing or invalid arguments, unknown options: argparse-style exit 2.
- `--help`: exit 0, usage showing `--user` and `--status`; no order query.
- Importing `orders_cli` has no side effects: no orders queried, no output,
  no arguments parsed, no fixture mutation.

## Limits

- Standard library only (`argparse`, `json`, `sys`).
- Only `pending` and `shipped` status values are accepted.
- Fixture caller IDs are fictional, not real authentication.
- No provider or network calls belong in this project.