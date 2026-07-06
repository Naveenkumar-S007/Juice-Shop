# Copyright (c) 2026, Your Company
# License: MIT
"""
Hooks for ERPNext Sales Invoice / POS Invoice that automatically deduct
raw material stock based on the Juice Recipe linked to each item.

This replaces the old custom Juice Order flow with the standard
ERPNext Sales Invoice + POS Invoice workflow.
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime


def on_sales_invoice_submit(doc, method=None):
	"""Called via hooks.py doc_event on Sales Invoice on_submit.
	Deducts raw material stock for each invoice item that has a Juice Recipe."""
	if not _has_recipe_items(doc):
		return
	deduct_stock_for_invoice(doc)


def on_sales_invoice_cancel(doc, method=None):
	"""Called via hooks.py doc_event on Sales Invoice on_cancel.
	Restores raw material stock for each invoice item that has a Juice Recipe."""
	if not _has_recipe_items(doc):
		return
	restore_stock_for_cancellation(doc)


def _has_recipe_items(doc):
	"""Quick check if any item on the invoice has a Juice Recipe."""
	for row in doc.get("items"):
		if frappe.db.exists("Juice Recipe", {"item": row.item_code, "disabled": 0}):
			return True
	return False


def deduct_stock_for_invoice(doc):
	"""
	For each item row on the Sales Invoice, look up the Juice Recipe
	and deduct the corresponding raw material stock.
	Wrapped in a savepoint so any failure undoes the entire batch.
	"""
	frappe.db.savepoint("before_sales_stock_deduction")
	try:
		for row in doc.get("items"):
			recipe = frappe.db.get_value(
				"Juice Recipe",
				{"item": row.item_code, "disabled": 0},
				"name",
			)
			if not recipe:
				continue

			recipe_rows = frappe.get_all(
				"Juice Recipe Item",
				filters={"parent": recipe, "parenttype": "Juice Recipe"},
				fields=["raw_material", "quantity_per_unit"],
			)

			for ing in recipe_rows:
				required_qty = flt(ing.quantity_per_unit) * flt(row.qty)
				material = frappe.get_doc(
					"Raw Material", ing.raw_material, for_update=True
				)

				if flt(material.current_stock) < required_qty:
					frappe.throw(
						_("Insufficient stock of {0}. Required: {1}, Available: {2}").format(
							material.material_name, required_qty, material.current_stock
						)
					)

				material.current_stock = flt(material.current_stock) - required_qty
				material.save(ignore_permissions=True)

				frappe.get_doc(
					{
						"doctype": "Stock Ledger Entry",
						"raw_material": material.name,
						"change_qty": -required_qty,
						"balance_after": material.current_stock,
						"reference_doctype": "Sales Invoice",
						"reference_name": doc.name,
						"posting_datetime": now_datetime(),
						"remarks": _("Deducted for {0} x {1} (Invoice {2})").format(
							row.qty, row.item_code, doc.name
						),
					}
				).insert(ignore_permissions=True)

				if material.current_stock < flt(material.reorder_level):
					frappe.publish_realtime(
						"low_stock_alert",
						{
							"material": material.material_name,
							"stock": material.current_stock,
						},
						user="System Manager",
					)
	except Exception:
		frappe.db.rollback(save_point="before_sales_stock_deduction")
		raise


def restore_stock_for_cancellation(doc):
	"""Reverse the stock deduction when a Sales Invoice is cancelled."""
	for row in doc.get("items"):
		recipe = frappe.db.get_value(
			"Juice Recipe",
			{"item": row.item_code, "disabled": 0},
			"name",
		)
		if not recipe:
			continue

		recipe_rows = frappe.get_all(
			"Juice Recipe Item",
			filters={"parent": recipe, "parenttype": "Juice Recipe"},
			fields=["raw_material", "quantity_per_unit"],
		)

		for ing in recipe_rows:
			restore_qty = flt(ing.quantity_per_unit) * flt(row.qty)
			material = frappe.get_doc(
				"Raw Material", ing.raw_material, for_update=True
			)
			material.current_stock = flt(material.current_stock) + restore_qty
			material.save(ignore_permissions=True)

			frappe.get_doc(
				{
					"doctype": "Stock Ledger Entry",
					"raw_material": material.name,
					"change_qty": restore_qty,
					"balance_after": material.current_stock,
					"reference_doctype": "Sales Invoice",
					"reference_name": doc.name,
					"posting_datetime": now_datetime(),
				"remarks": _("Reversed due to cancellation of Invoice {0}").format(
					doc.name
				),
			}
		).insert(ignore_permissions=True)


def on_item_update(doc, method=None):
	"""Called via hooks.py doc_event on Item on_update.
	If the Item has ingredients in its recipe_ingredients table,
	auto-create or update the corresponding Juice Recipe.
	"""
	ingredients = doc.get("recipe_ingredients") or []

	if not ingredients:
		# No ingredients on this Item — leave any existing Juice Recipe alone
		return

	# Find existing Juice Recipe for this item (including disabled ones)
	recipe_name = frappe.db.get_value(
		"Juice Recipe", {"item": doc.name}, "name"
	)

	if recipe_name:
		recipe = frappe.get_doc("Juice Recipe", recipe_name)
		# Re-enable if it was disabled
		recipe.disabled = 0
	else:
		# Prevent duplicate naming conflict if a deleted recipe's name still lingers
		if frappe.db.exists("Juice Recipe", {"item": doc.name}):
			# Shouldn't happen after the check above, but safety net
			return
		recipe = frappe.get_doc({
			"doctype": "Juice Recipe",
			"item": doc.name,
		})

	# Clear existing ingredients and re-populate from Item's table
	recipe.set("ingredients", [])
	for ing in ingredients:
		recipe.append("ingredients", {
			"raw_material": ing.get("raw_material"),
			"quantity_per_unit": ing.get("quantity_per_unit"),
		})

	recipe.save(ignore_permissions=True)
