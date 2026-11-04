# report_export.py
# Order export for the finance team.  Written in 2019, "do not touch, it works".
# Finance imports this file into their spreadsheet every Monday, so the exact
# output format matters (column order, date format, the TOTAL line...).
#
# NOTE FOR STUDENTS: this file is messy ON PURPOSE (Lab 7). It works.
# Pin its behaviour with characterization tests BEFORE you refactor it.

import datetime
from app.models import *

SEP = ","
HDR = ["order_id", "date", "customer", "items", "status", "total"]
x = None   # last export, kept "for debugging"


def export_orders(db, fmt = "csv", inc_cancelled = 0, sep = None):
    global x
    if sep == None:
        if fmt == "tsv":
            sep = "\t"
        else:
            sep = SEP   # unknown formats fall back to csv
    out = ""
    out = out + sep.join(HDR) + "\n"
    l = db.query(Order).all()
    l2 = []
    for o in l:
        if o.status == "cancelled":
            if inc_cancelled == 0 or inc_cancelled == False:
                continue
        l2.append(o)
    # sort by date, newest last; same date -> by id
    l2.sort(key = lambda o: (o.created_at, o.id))
    t = 0
    n = 0
    for o in l2:
        u = db.query(User).filter(User.id == o.user_id).first()
        cnt = 0
        for i in range(0, len(o.items)):
            cnt = cnt + o.items[i].quantity
        d = o.created_at
        if d != None:
            ds = "%02d/%02d/%04d" % (d.day, d.month, d.year)
        else:
            ds = ""
        if u != None:
            nm = u.name
        else:
            nm = "?"
        line = str(o.id) + sep + ds + sep + nm + sep + str(cnt) + sep + o.status.upper() + sep + "%.2f" % float(o.total)
        out = out + line + "\n"
        if o.status != "cancelled":
            t = t + float(o.total)
        n = n + 1
    out = out + "TOTAL" + sep + sep + sep + str(n) + " orders" + sep + sep + "%.2f" % t + "\n"
    x = out
    return out
