# Juice Shop (Frappe/ERPNext Custom App)

A Frappe/ERPNext app that extends **Sales Invoice / POS Invoice** with
automatic raw-material stock deduction via **Juice Recipes**. Uses
the standard ERPNext selling workflow — no custom order doctypes needed.

## What this app adds

1. **Raw Material** doctype — your ingredient master (Orange, Sugar, Ice,
   etc.) with unit of measure, cost per unit, current stock
   (auto-updated), and reorder level.
2. **Juice Recipe** doctype — one recipe per ERPNext **Item**, defining
   which raw materials (and how much of each) go into ONE unit of that item.
3. **Automatic stock deduction via Sales Invoice** — when a **Sales
   Invoice** or **POS Invoice** is submitted, for every item that has a
   Juice Recipe, the app automatically deducts the required raw material
   stock. Cancelling the invoice restores the stock back.
4. **Waste Entry** doctype — log spoiled/wasted **raw materials**
   directly (e.g. spoiled oranges, spilled sugar, melted ice) before
   they are ever used in a juice. Waste value is calculated automatically
   from each raw material's cost per unit.
5. **Waste Reason** doctype — a simple, editable list of waste reasons
   (e.g. "Spoilage", "Spillage", "Unsold at close").
6. **Stock Adjustment** — a submittable doctype for restocking raw
   materials or correcting stock levels. Submitting adds stock;
   cancelling reverses it.
7. **Stock Ledger Entry** — an automatic, read-only audit trail of every
   raw material stock movement (which invoice/waste/adjustment caused it,
   how much changed, and the resulting balance) for full traceability.
8. **Raw Material Stock Report** — shows current stock, reorder level,
   and a "Below Reorder Level" indicator for every active raw material.
9. **Daily Juice Sales** report — quantity sold and revenue per item from
   submitted Sales Invoices.
10. **Daily Waste Summary** report — wasted quantity and value per raw
    material and reason from submitted Waste Entries.

## How automatic stock deduction works

Example: "Orange Juice" (a standard ERPNext Item) has a Juice Recipe —

| Raw Material | Quantity (per serving) |
|---|---|
| Orange | 3 pieces |
| Sugar | 20 grams |
| Ice | 50 grams |

When a **Sales Invoice** is submitted for **2 Orange Juices**, the app
automatically deducts:

- Orange: 3 x 2 = **6 pieces** deducted from stock
- Sugar: 20 x 2 = **40 grams** deducted from stock
- Ice: 50 x 2 = **100 grams** deducted from stock

Each deduction is written to **Stock Ledger Entry** so you can see exactly
which invoice consumed which ingredient and when. If the invoice is later
cancelled, the same quantities are automatically added back to stock.

Items with no Juice Recipe defined are simply ignored — no deduction occurs.
Define a recipe via **Juice Recipe → New** and link it to your Item.

### Key design features

- **Standard ERPNext accounting**: Uses Sales Invoice / POS Invoice for
  full accounting (debtors, income accounts, taxes, payments) — no custom
  order doctype needed.
- **Atomic deductions**: Stock deduction is wrapped in a database savepoint
  so that if ANY ingredient is insufficient, the entire operation is
  rolled back — no partial deductions.
- **Row-level locking**: Raw Materials are fetched with `for_update=True`
  inside deduction loops to prevent race conditions.
- **Low-stock alerts**: A real-time notification fires whenever a
  material's current stock drops below its reorder level.
- **Unified ledger**: Every stock movement — sale, waste, restock, or any
  reversal on cancel — writes to Stock Ledger Entry in the same format,
  tagged only by a different Reference Doctype ("Sales Invoice",
  "Waste Entry", "Stock Adjustment").

## Installation

```bash
# from your bench directory
bench get-app juice_shop https://github.com/Naveenkumar-S007/Juice-Shop.git
bench --site your-site.local install-app juice_shop
bench --site your-site.local migrate
bench restart
```

## Typical flow

1. Set up your ingredients once in **Raw Material** (e.g. Orange, Sugar,
   Ice) with a unit of measure, current stock, and cost per unit.
2. Set up your menu as standard ERPNext **Items** (e.g. "Orange Juice").
3. Create a **Juice Recipe** for each item, linking the item to its
   required raw materials and quantities.
4. When a customer orders, create a **Sales Invoice** or use **POS
   Invoice** as usual. Raw material stock is deducted automatically
   on submit.
5. When raw materials are spoiled or spilled, create a **Waste Entry**
   selecting the wasted raw material directly and submit.
6. When new stock arrives, create a **Stock Adjustment**, add the
   materials and quantities, and submit to increase stock.
7. Use the **Raw Material Stock Report** to see what needs reordering, or
   the **Daily Juice Sales** and **Daily Waste Summary** reports at the
   end of the day.
