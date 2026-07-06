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
		self.deduct_raw_material_stock()
		self.status = "Submitted"

	def on_cancel(self):
		self.status = "Cancelled"
		self.restore_stock_for_cancellation()

	def deduct_raw_material_stock(self):
		"""
		Deduct raw material stock directly for each waste entry row.
		Waste happens BEFORE ingredients are ever turned into juice
		(e.g. spoiled oranges, spilled sugar, melted ice), so we
		deduct the Raw Material itself — no Juice Recipe lookup.
		Wrapped in a savepoint so any failure undoes the entire batch.
		"""
		frappe.db.savepoint("before_waste_deduction")
		try:
			for row in self.items:
				material = frappe.get_doc(
					"Raw Material", row.raw_material, for_update=True
				)

				if flt(material.current_stock) < flt(row.qty):
					frappe.throw(
						_("Cannot waste {0} of {1} — only {2} in stock.").format(
							row.qty, material.material_name, material.current_stock
						)
					)

				material.current_stock = flt(material.current_stock) - flt(row.qty)
				material.save(ignore_permissions=True)

				frappe.get_doc(
					{
						"doctype": "Stock Ledger Entry",
						"raw_material": material.name,
						"change_qty": -flt(row.qty),
						"balance_after": material.current_stock,
						"reference_doctype": "Waste Entry",
						"reference_name": self.name,
						"posting_datetime": now_datetime(),
						"remarks": _("Wasted: {0} ({1} {2})").format(
							row.reason, row.qty, material.unit_of_measure
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
		"""Reverse the stock deduction when a Waste Entry is cancelled.
		Adds the wasted qty back to each Raw Material's current_stock
		and writes a reversing Stock Ledger Entry."""
		for row in self.items:
			material = frappe.get_doc(
				"Raw Material", row.raw_material, for_update=True
			)
			material.current_stock = flt(material.current_stock) + flt(row.qty)
			material.save(ignore_permissions=True)

			frappe.get_doc(
				{
					"doctype": "Stock Ledger Entry",
					"raw_material": material.name,
					"change_qty": flt(row.qty),
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
