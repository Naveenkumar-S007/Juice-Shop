# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class StockAdjustment(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		total_qty = 0.0
		for row in self.items:
			total_qty += flt(row.qty)
		self.total_qty = total_qty

	def on_submit(self):
		self.status = "Submitted"
		self.update_stock(direction=1)

	def on_cancel(self):
		self.status = "Cancelled"
		self.update_stock(direction=-1)

	def update_stock(self, direction):
		"""Restock (direction=+1) or reverse-restock (direction=-1) raw
		material stock. Each row in the items child table adjusts a single
		raw material and writes a Stock Ledger Entry."""
		for row in self.items:
			material = frappe.get_doc("Raw Material", row.raw_material, for_update=True)
			qty_change = flt(row.qty) * direction

			if qty_change < 0 and material.current_stock < abs(qty_change):
				frappe.throw(
					_("Cannot reverse {0} of {1} — only {2} in stock.").format(
						abs(qty_change), material.material_name, material.current_stock
					)
				)

			material.current_stock = flt(material.current_stock) + qty_change
			material.save(ignore_permissions=True)

			remarks = _("Restocked via {0}: {1}").format(self.name, row.remarks or "")
			if direction < 0:
				remarks = _("Reversed restock via {0}: {1}").format(self.name, row.remarks or "")

			frappe.get_doc(
				{
					"doctype": "Stock Ledger Entry",
					"raw_material": material.name,
					"change_qty": qty_change,
					"balance_after": material.current_stock,
					"reference_doctype": "Stock Adjustment",
					"reference_name": self.name,
					"posting_datetime": now_datetime(),
					"remarks": remarks,
				}
			).insert(ignore_permissions=True)
