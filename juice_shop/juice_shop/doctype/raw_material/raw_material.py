# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class RawMaterial(Document):
	def validate(self):
		# Ensure current_stock never goes negative
		if flt(self.current_stock) < 0:
			frappe.throw(
				f"Stock of {self.material_name} cannot go below zero. "
				f"Current balance: {self.current_stock}"
			)


def adjust_stock(raw_material, qty_change, voucher_type, voucher_no, remarks=None):
	"""Increase or decrease a Raw Material's current_stock and write a
	Stock Ledger Entry. Uses for_update=True (row-level lock) to prevent
	race conditions.

	qty_change should be NEGATIVE to consume stock (sale/waste) and
	POSITIVE to add stock back (reversal or restock).
	"""
	if not raw_material or not qty_change:
		return

	material = frappe.get_doc("Raw Material", raw_material, for_update=True)

	if qty_change < 0 and flt(material.current_stock) < abs(qty_change):
		frappe.throw(
			f"Not enough stock of {material.material_name}. "
			f"Required: {abs(qty_change)}, Available: {material.current_stock}"
		)

	new_balance = flt(material.current_stock) + flt(qty_change)
	material.current_stock = new_balance
	material.save(ignore_permissions=True)

	frappe.get_doc(
		{
			"doctype": "Stock Ledger Entry",
			"raw_material": raw_material,
			"posting_datetime": now_datetime(),
			"reference_doctype": voucher_type,
			"reference_name": voucher_no,
			"change_qty": flt(qty_change),
			"balance_after": new_balance,
			"remarks": remarks,
		}
	).insert(ignore_permissions=True)

	# Low-stock alert
	if material.current_stock < flt(material.reorder_level):
		frappe.publish_realtime(
			"low_stock_alert",
			{"material": material.material_name, "stock": material.current_stock},
			user="System Manager",
		)

	return new_balance
