# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class WasteEntry(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		total_qty = 0
		total_value = 0.0
		for row in self.items:
			row.amount = flt(row.qty) * flt(row.cost_rate)
			total_qty += flt(row.qty)
			total_value += flt(row.amount)
		self.total_qty = total_qty
		self.total_waste_value = total_value

	def on_submit(self):
		self.deduct_stock_for_waste()
		self.status = "Submitted"

	def on_cancel(self):
		self.status = "Cancelled"
		self.restore_stock_for_cancellation()

	def deduct_stock_for_waste(self):
		"""Look up each wasted juice item's recipe and deduct the
		corresponding raw material stock. Wrapped in a savepoint so
		any failure undoes the entire batch."""
		frappe.db.savepoint("before_waste_deduction")
		try:
			for row in self.items:
				recipe_rows = frappe.get_all(
					"Juice Recipe Item",
					filters={"parent": row.juice_item, "parenttype": "Juice Item"},
					fields=["raw_material", "quantity_per_unit"],
				)
				if not recipe_rows:
					frappe.throw(
						_("No recipe defined for {0}. Cannot process waste.").format(
							row.juice_item
						)
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
							"reference_doctype": "Waste Entry",
							"reference_name": self.name,
							"posting_datetime": now_datetime(),
							"remarks": _("Wasted: {0} ({1} x {2})").format(
								row.reason, row.qty, row.juice_item
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
			frappe.db.rollback(save_point="before_waste_deduction")
			raise

	def restore_stock_for_cancellation(self):
		"""Reverse the stock deduction when a Waste Entry is cancelled."""
		for row in self.items:
			recipe_rows = frappe.get_all(
				"Juice Recipe Item",
				filters={"parent": row.juice_item, "parenttype": "Juice Item"},
				fields=["raw_material", "quantity_per_unit"],
			)
			if not recipe_rows:
				continue

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
						"reference_doctype": "Waste Entry",
						"reference_name": self.name,
						"posting_datetime": now_datetime(),
						"remarks": _("Reversed waste entry {0}").format(self.name),
					}
				).insert(ignore_permissions=True)


def on_waste_entry_submit(doc, method=None):
	"""hooks.py doc_event: simple confirmation on submit."""
	frappe.msgprint(
		_("Waste Entry {0} submitted. Waste value: {1}").format(
			doc.name, doc.total_waste_value
		),
		alert=True,
		indicator="orange",
	)
