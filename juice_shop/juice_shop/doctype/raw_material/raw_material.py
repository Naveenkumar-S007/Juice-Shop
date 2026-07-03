# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class RawMaterial(Document):
	def before_insert(self):
		# Seed Current Stock from Opening Stock the first time this
		# material is created.
		if not self.current_stock:
			self.current_stock = flt(self.opening_stock)


def adjust_stock(raw_material, qty_change, voucher_type, voucher_no, remarks=None):
	"""Increase or decrease a Raw Material's Current Stock and write a
	Stock Ledger Entry so every movement is traceable.

	qty_change should be NEGATIVE to consume stock (e.g. a sale) and
	POSITIVE to add stock back (e.g. cancelling a sale, or a restock).
	"""
	if not raw_material or not qty_change:
		return

	current_stock = flt(frappe.db.get_value("Raw Material", raw_material, "current_stock"))
	new_balance = current_stock + flt(qty_change)

	# Update the balance directly - fast, and avoids re-running Raw
	# Material's own validate/save side effects for a simple stock tick.
	frappe.db.set_value("Raw Material", raw_material, "current_stock", new_balance)

	frappe.get_doc(
		{
			"doctype": "Stock Ledger Entry",
			"raw_material": raw_material,
			"posting_datetime": now_datetime(),
			"voucher_type": voucher_type,
			"voucher_no": voucher_no,
			"qty_change": qty_change,
			"balance_qty": new_balance,
			"remarks": remarks,
		}
	).insert(ignore_permissions=True)

	return new_balance
