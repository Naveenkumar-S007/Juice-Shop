# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


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
		if self.status == "Pending":
			self.status = "Served"
		self.update_raw_material_stock(direction=-1)

	def on_cancel(self):
		self.status = "Cancelled"
		self.update_raw_material_stock(direction=1)

	def update_raw_material_stock(self, direction):
		"""Consume (direction=-1) or restore (direction=+1) raw material
		stock based on each ordered juice's recipe (Juice Item > Recipe
		Items), multiplied by the quantity ordered. Juices with no recipe
		defined are skipped, so this stays fully backward compatible."""
		from juice_shop.juice_shop.doctype.raw_material.raw_material import adjust_stock

		for row in self.items:
			recipe_rows = frappe.get_all(
				"Juice Recipe Item",
				filters={"parent": row.juice_item, "parenttype": "Juice Item"},
				fields=["raw_material", "qty_required"],
			)
			for recipe_row in recipe_rows:
				qty_change = flt(recipe_row.qty_required) * flt(row.qty) * direction
				remarks = _("{0} x {1} ({2})").format(row.juice_item, row.qty, self.name)
				adjust_stock(
					raw_material=recipe_row.raw_material,
					qty_change=qty_change,
					voucher_type="Juice Order",
					voucher_no=self.name,
					remarks=remarks,
				)


def on_juice_order_submit(doc, method=None):
	"""hooks.py doc_event: simple confirmation on submit. Raw material
	stock deduction itself happens in JuiceOrder.on_submit(); this just
	shows the counter staff a confirmation toast."""
	frappe.msgprint(
		_("Order {0} submitted. Total: {1}").format(doc.name, doc.total_amount),
		alert=True,
		indicator="green",
	)
