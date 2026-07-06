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
   etc.) with unit of measure, cost per unit, current stock
   (auto-updated), and reorder level.
8. **Recipe (Ingredients)** — each **Juice Item** has a Recipe Items
   child table where you define what raw materials (and how much of each)
   go into ONE unit of that juice.
9. **Automatic stock deduction** — when a **Juice Order** or **Waste
   Entry** is submitted, the app looks up the recipe for every juice on
   the bill, multiplies it by the quantity, and deducts that much from
   each raw material's Current Stock. Cancelling automatically restores
   the stock back.
10. **Stock Adjustment** — a submittable doctype for restocking raw
    materials or correcting stock levels. Submitting adds stock;
    cancelling reverses it.
11. **Stock Ledger Entry** — an automatic, read-only audit trail of every
    raw material stock movement (which order/waste/adjustment caused it,
    how much changed, and the resulting balance) for full traceability.
12. **Raw Material Stock Report** — shows current stock, reorder level,
    and a "Below Reorder Level" indicator for every active raw material.

## How automatic stock deduction works

Example: "Orange Juice" has this recipe defined —

| Raw Material | Quantity (per serving) |
|---|---|
| Orange | 3 pieces |
| Sugar | 20 grams |
| Ice | 50 grams |

If a customer orders **2 Orange Juices** and the Juice Order is submitted,
the app automatically deducts:

- Orange: 3 x 2 = **6 pieces** deducted from stock
- Sugar: 20 x 2 = **40 grams** deducted from stock
- Ice: 50 x 2 = **100 grams** deducted from stock

Each deduction is written to **Stock Ledger Entry** so you can see exactly
which order consumed which ingredient and when. If the order is later
cancelled, the same quantities are automatically added back to stock.

Juice Items with no recipe defined cannot be ordered or wasted — the app
will throw an error. Define a recipe on each active Juice Item.

### Key design features

- **Atomic deductions**: Stock deduction is wrapped in a database savepoint
  so that if ANY ingredient is insufficient, the entire operation is
  rolled back — no partial deductions.
- **Row-level locking**: Raw Materials are fetched with `for_update=True`
  inside deduction loops to prevent race conditions.
- **Low-stock alerts**: A real-time notification fires whenever a
  material's current stock drops below its reorder level.
- **Unified ledger**: Every stock movement — sale, waste, restock, or any
  reversal on cancel — writes to Stock Ledger Entry in the same format,
  tagged only by a different Reference Doctype.

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
   Ice) with a unit of measure, current stock, and cost per unit.
2. Set up your menu in **Juice Item** (e.g. "Orange Juice") and define
   its **Recipe Items** — which raw materials, and how much of each,
   make one serving.
3. When a customer orders, create a **Juice Order**, add the juice(s),
   and submit. Raw material stock is deducted automatically.
4. When juice is spoiled or unsold, create a **Waste Entry** and submit.
   Raw material stock is deducted automatically.
5. When new stock arrives, create a **Stock Adjustment**, add the
   materials and quantities, and submit to increase stock.
6. Use the **Raw Material Stock Report** to see what needs reordering, or
   the **Daily Juice Sales** and **Daily Waste Summary** reports at the
   end of the day.
