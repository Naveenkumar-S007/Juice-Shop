# Copyright (c) 2026, Your Company
# License: MIT
"""
Raw Material Stock Report: shows the current stock level for every active
raw material, alongside its reorder level, and flags materials that need
reordering.
"""

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data


def get_columns():
	return [
		{
			"label": _("Material Name"),
			"fieldname": "material_name",
			"fieldtype": "Link",
			"options": "Raw Material",
			"width": 200,
		},
		{
			"label": _("Unit of Measure"),
			"fieldname": "unit_of_measure",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Current Stock"),
			"fieldname": "current_stock",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Reorder Level"),
			"fieldname": "reorder_level",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Below Reorder Level"),
			"fieldname": "below_reorder",
			"fieldtype": "Data",
			"width": 160,
		},
	]


def get_data():
	raw_materials = frappe.get_all(
		"Raw Material",
		filters={"is_active": 1},
		fields=["name", "material_name", "unit_of_measure", "current_stock", "reorder_level"],
		order_by="material_name asc",
	)

	data = []
	for rm in raw_materials:
		below_reorder = "Yes" if (rm.current_stock or 0) < (rm.reorder_level or 0) else "No"
		data.append(
			{
				"material_name": rm.name,
				"unit_of_measure": rm.unit_of_measure,
				"current_stock": rm.current_stock,
				"reorder_level": rm.reorder_level,
				"below_reorder": below_reorder,
			}
		)

	return data
