# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class JuiceOrder(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		total_qty = 0
		total_amount = 0.0
		for row in self.items:
			row.amount = flt(row.qty) * flt(row.rate)
			total_qty += flt(row.qty)
			total_amount += flt(row.amount)
		self.total_qty = total_qty
		self.total_amount = total_amount

	def on_submit(self):
		self.deduct_stock_for_order()
		if self.status == "Pending":
			self.status = "Served"

	def on_cancel(self):
		self.status = "Cancelled"
		self.restore_stock_for_cancellation()

	def deduct_stock_for_order(self):
		"""Look up each ordered juice's recipe (inline on Juice Item),
		deduct raw material stock, and write Stock Ledger Entries.
		Wrapped in a savepoint so any failure undoes the entire batch."""
		frappe.db.savepoint("before_stock_deduction")
		try:
			for row in self.items:
				recipe_rows = frappe.get_all(
					"Juice Recipe Item",
					filters={"parent": row.juice_item, "parenttype": "Juice Item"},
					fields=["raw_material", "quantity_per_unit"],
				)
				if not recipe_rows:
					frappe.throw(
						_("No recipe defined for {0}. Cannot fulfill order.").format(
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
							"reference_doctype": "Juice Order",
							"reference_name": self.name,
							"posting_datetime": now_datetime(),
							"remarks": _("Deducted for {0} x {1}").format(
								row.qty, row.juice_item
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
			frappe.db.rollback(save_point="before_stock_deduction")
			raise

	def restore_stock_for_cancellation(self):
		"""Reverse the stock deduction when an order is cancelled."""
		for row in self.items:
			recipe_rows = frappe.get_all(
				"Juice Recipe Item",
				filters={"parent": row.juice_item, "parenttype": "Juice Item"},
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
						"reference_doctype": "Juice Order",
						"reference_name": self.name,
						"posting_datetime": now_datetime(),
						"remarks": _("Reversed due to cancellation of {0}").format(
							self.name
						),
					}
				).insert(ignore_permissions=True)


def on_juice_order_submit(doc, method=None):
	"""hooks.py doc_event: simple confirmation on submit."""
	frappe.msgprint(
		_("Order {0} submitted. Total: {1}").format(doc.name, doc.total_amount),
		alert=True,
		indicator="green",
	)
