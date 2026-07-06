# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class JuiceItem(Document):
	def validate(self):
		if self.is_active and not self.get("recipe_items"):
			frappe.throw(
				_("Juice Item '{0}' is marked as Active but has no Recipe Items defined. "
				  "Add at least one raw material to the Recipe (Ingredients) section, "
				  "or deactivate this item.").format(self.item_name)
			)
		for row in self.get("recipe_items") or []:
			if flt(row.quantity_per_unit) <= 0:
				frappe.throw(
					_("Row #{0}: Quantity per unit must be greater than 0 for raw material '{1}'.").format(
						row.idx, row.raw_material
					)
				)
