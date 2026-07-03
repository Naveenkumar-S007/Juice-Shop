# Copyright (c) 2026, Your Company
# License: MIT
"""
Simple waste report: for a date range, shows wasted quantity and value per
juice item and reason, from submitted Waste Entries.
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
		{"label": _("Juice Item"), "fieldname": "juice_item", "fieldtype": "Link", "options": "Juice Item", "width": 180},
		{"label": _("Reason"), "fieldname": "reason", "fieldtype": "Link", "options": "Waste Reason", "width": 150},
		{"label": _("Entries"), "fieldname": "entry_count", "fieldtype": "Int", "width": 90},
		{"label": _("Qty Wasted"), "fieldname": "qty_wasted", "fieldtype": "Int", "width": 100},
		{"label": _("Waste Value"), "fieldname": "waste_value", "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	from_date = filters.get("from_date") or add_days(nowdate(), -7)
	to_date = filters.get("to_date") or nowdate()

	return frappe.db.sql(
		"""
		select
			wi.juice_item as juice_item,
			wi.reason as reason,
			count(distinct w.name) as entry_count,
			sum(wi.qty) as qty_wasted,
			sum(wi.amount) as waste_value
		from `tabWaste Entry Item` wi
		inner join `tabWaste Entry` w on w.name = wi.parent
		where w.docstatus = 1
			and w.waste_date between %(from_date)s and %(to_date)s
		group by wi.juice_item, wi.reason
		order by waste_value desc
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
