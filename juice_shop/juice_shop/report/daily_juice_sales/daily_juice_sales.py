# Copyright (c) 2026, Your Company
# License: MIT
"""
Daily Sales report: for a date range, shows quantity sold and revenue
per item, from submitted Sales Invoices. Uses standard ERPNext Sales
Invoice Item table — no custom Juice Order doctype needed.
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 200},
		{"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 100},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 100},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	from_date = filters.get("from_date") or add_days(nowdate(), -7)
	to_date = filters.get("to_date") or nowdate()

	return frappe.db.sql(
		"""
		select
			si.item_code as item_code,
			count(distinct si.parent) as invoice_count,
			sum(si.qty) as qty_sold,
			sum(si.base_net_amount) as revenue
		from `tabSales Invoice Item` si
		inner join `tabSales Invoice` inv on inv.name = si.parent
		where inv.docstatus = 1
			and inv.posting_date between %(from_date)s and %(to_date)s
		group by si.item_code
		order by revenue desc
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
