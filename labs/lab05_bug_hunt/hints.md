# Lab 5 hints, by area

`grade.py` tells you the area of each bug you haven't fixed yet. Open one level at a time:
level 1 is a question to ask, level 2 is an experiment to run, level 3 says where to read.
Try for at least 10 minutes before you open level 3.

## Orders
*(2 bugs)*

<details><summary>Level 1</summary>

Who may see an order, and what may happen to it after it leaves the warehouse?
</details>
<details><summary>Level 2</summary>

Place an order as Ana. Try every orders endpoint as Ben too. Then ship the order as admin and try everything again as Ana.
</details>
<details><summary>Level 3</summary>

Read `app/routers/orders.py` endpoint by endpoint and compare each with the rules at the top of the file and the status list in `app/models.py`.
</details>

## Products
*(1 bug)*

<details><summary>Level 1</summary>

If you page through the whole catalogue, do you see every product exactly once?
</details>
<details><summary>Level 2</summary>

List with `page_size=2` and write down the ids, page by page. Compare with one big page (`page_size=50`). Read the README's endpoint table carefully.
</details>
<details><summary>Level 3</summary>

Read `list_products` in `app/routers/products.py`, especially the parameters.
</details>

## Money
*(2 bugs)*

<details><summary>Level 1</summary>

Do the totals match a calculator, to the cent, for every price and with every coupon?
</details>
<details><summary>Level 2</summary>

Add products with awkward prices (like 1.15 or 2.05) as admin and order them. Then place an order with a coupon and compare it with `/coupons/preview` for the same items.
</details>
<details><summary>Level 3</summary>

Read the rules at the top of `app/services/pricing.py`, then check every function in that file and the pricing part of `create_order`.
</details>

## Coupons & time
*(1 bug)*

<details><summary>Level 1</summary>

The shop's admin works in Seoul (UTC+9). When does their coupon really expire?
</details>
<details><summary>Level 2</summary>

As admin, create coupons whose `expires_at` ends in `+09:00`, a few hours either side of "now". Which ones are accepted? Tests freeze "now" with `get_now`.
</details>
<details><summary>Level 3</summary>

Follow `expires_at` from the request to the database and back: `app/schemas.py`, `app/db.py`, `app/services/coupons.py`.
</details>

## Input checks
*(1 bug)*

<details><summary>Level 1</summary>

What is the strangest order a customer could send?
</details>
<details><summary>Level 2</summary>

Send orders with unusual numbers, then check the totals and the product stock.
</details>
<details><summary>Level 3</summary>

Read the request models in `app/schemas.py` and compare their limits with the business rules.
</details>

## Login
*(1 bug)*

<details><summary>Level 1</summary>

People don't always type their email the same way twice.
</details>
<details><summary>Level 2</summary>

Log in as Ana with her email typed in different ways.
</details>
<details><summary>Level 3</summary>

Read `app/auth.py` and look at how emails are stored in `seed.py`.
</details>

## Reviews
*(2 bugs)*

<details><summary>Level 1</summary>

Who is allowed to write a review, and does a review stay once it's written?
</details>
<details><summary>Level 2</summary>

As Ben, try to review products he did and didn't buy. After any `201 Created`, list the reviews for that product.
</details>
<details><summary>Level 3</summary>

Read `app/routers/reviews.py` from top to bottom, and the docstring of `get_db` in `app/db.py`.
</details>
