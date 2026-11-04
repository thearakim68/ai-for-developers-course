"""Lab 7 starter: characterization tests for app/legacy/report_export.py.

They pin what the code DOES today, not what it should do.
Copy this file into shopapi/tests/ and fill in the TODOs.
"""
from tests.conftest import ADMIN


def export(client, **params):
    r = client.get("/admin/reports/orders-export", headers=ADMIN, params=params)
    assert r.status_code == 200
    return r.text


def test_csv_export_of_the_demo_data(client):
    # Example: the whole output, exactly. One changed character fails the test.
    assert export(client) == (
        "order_id,date,customer,items,status,total\n"
        "10,02/05/2026,Ana,1,PAID,54.89\n"
        "11,03/05/2026,Ben,2,PAID,43.78\n"
        "12,04/05/2026,Ana,3,SHIPPED,52.47\n"
        "TOTAL,,,3 orders,,151.14\n"
    )


# TODO: tsv format (what separator? same columns?)
# TODO: include_cancelled=true: which rows change? does the TOTAL amount change? the order count?
# TODO: orders on the same date: what order do they come out in?
# TODO: export_orders(db, "xml") called directly: what happens with an unknown format?
# TODO: a customer whose name contains a comma (add a user in the test): pin what happens today
