# Juice Shop (Frappe/ERPNext Custom App)

A small, simple app for a juice shop counter: keep a menu of juices, log each
order as a customer buys it, and see daily sales. No manufacturing, no batch
traceability, no warehouse/BOM logic — just day-to-day sales tracking.

## What this app adds

1. **Juice Item** doctype — your menu master (name, category, size, selling
   price, cost price, active/inactive).
2. **Juice Order** doctype — one entry per customer order. Add one or more
   juices (via the **Juice Order Item** child table), and the total is
   calculated automatically. Track payment mode and status (Pending /
   Preparing / Served / Cancelled).
3. **Daily Juice Sales** report — pick a date range and see total orders,
   quantity sold, and revenue, broken down by juice item.
4. **Waste Entry** doctype — log spoiled/wasted juice (spillage, expired
   fruit, unsold stock, etc.) with quantity and reason, per **Waste Entry
   Item** row. Waste value is calculated automatically from each item's
   cost price.
5. **Waste Reason** doctype — a simple, editable list of waste reasons
   (e.g. "Spoilage", "Spillage", "Unsold at close").
6. **Daily Waste Summary** report — pick a date range and see wasted
   quantity and value, broken down by juice item and reason.
7. **Raw Material** doctype — your ingredient master (Orange, Sugar, Ice,
   etc.) with unit of measure, opening stock, and a live current stock
   balance.
8. **Recipe (Ingredients)** — each **Juice Item** now has a Recipe Items
   child table where you define what raw materials (and how much of each)
   go into ONE unit of that juice.
9. **Automatic stock deduction** — when a **Juice Order** is submitted,
   the app looks up the recipe for every juice on the bill, multiplies it
   by the quantity sold, and automatically deducts that much from each
   raw material's Current Stock. Cancelling the order automatically adds
   the stock back.
10. **Stock Ledger Entry** — an automatic, read-only log of every raw
    material stock movement (which order caused it, how much changed, and
    the resulting balance) for full traceability.

## How the automatic stock deduction works

Example: "Orange Juice" has this recipe defined —

| Raw Material | Qty Required (per unit) |
|---|---|
| Orange | 3 |
| Sugar | 20 g |
| Ice | 50 g |

If a customer orders **2 Orange Juices** and the Juice Order is submitted,
the app automatically deducts:

- Orange: 3 × 2 = **6** deducted from stock
- Sugar: 20 × 2 = **40 g** deducted from stock
- Ice: 50 × 2 = **100 g** deducted from stock

Each deduction is written to **Stock Ledger Entry** so you can see exactly
which order consumed which ingredient and when. If the order is later
cancelled, the same quantities are automatically added back to stock.

Juice Items with no recipe defined are simply skipped — this keeps the
feature fully optional and backward compatible with items you don't want
to track ingredients for.

## Installation

```bash
# from your bench directory
bench get-app juice_shop /path/to/juice_shop   # or your github repo URL
bench --site your-site.local install-app juice_shop
bench --site your-site.local migrate
bench restart
```

## Typical flow

1. Set up your ingredients once in **Raw Material** (e.g. Orange, Sugar,
   Ice) with a unit of measure and opening stock quantity.
2. Set up your menu once in **Juice Item** (e.g. "Orange Juice", "Mango
   Shake", "Watermelon Cooler") with a selling price, cost price, and its
   **Recipe Items** (which raw materials, and how much of each, make one
   unit).
3. When a customer orders, create a **Juice Order**, add the juice(s) and
   quantities, pick payment mode, and submit. Raw material stock is
   deducted automatically based on the recipe.
4. When juice or fruit is spoiled, spilled, or left unsold, create a
   **Waste Entry**, add the item(s), quantity, and reason, and submit. The
   waste value is calculated from the item's cost price.
5. Use the **Daily Juice Sales** and **Daily Waste Summary** reports at the
   end of the day/week to see what sold, what was wasted, and the net
   picture.
