# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


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
		self.status = "Submitted"

	def on_cancel(self):
		self.status = "Cancelled"


def on_waste_entry_submit(doc, method=None):
	"""hooks.py doc_event: simple confirmation on submit. This app has no
	stock/warehouse module, so waste is just logged and valued - nothing
	else moves automatically."""
	frappe.msgprint(
		_("Waste Entry {0} submitted. Waste value: {1}").format(doc.name, doc.total_waste_value),
		alert=True,
		indicator="orange",
	)
