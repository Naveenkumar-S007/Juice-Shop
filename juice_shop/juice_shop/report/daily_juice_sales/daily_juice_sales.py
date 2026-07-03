# Copyright (c) 2026, Your Company
# License: MIT
"""
Simple daily sales report: for a date range, shows quantity sold and revenue
per juice item, from submitted Juice Orders. No stock/warehouse dependency.
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
		{"label": _("Juice Item"), "fieldname": "juice_item", "fieldtype": "Link", "options": "Juice Item", "width": 200},
		{"label": _("Orders"), "fieldname": "order_count", "fieldtype": "Int", "width": 100},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Int", "width": 100},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	from_date = filters.get("from_date") or add_days(nowdate(), -7)
	to_date = filters.get("to_date") or nowdate()

	return frappe.db.sql(
		"""
		select
			oi.juice_item as juice_item,
			count(distinct o.name) as order_count,
			sum(oi.qty) as qty_sold,
			sum(oi.amount) as revenue
		from `tabJuice Order Item` oi
		inner join `tabJuice Order` o on o.name = oi.parent
		where o.docstatus = 1
			and o.order_date between %(from_date)s and %(to_date)s
		group by oi.juice_item
		order by revenue desc
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
