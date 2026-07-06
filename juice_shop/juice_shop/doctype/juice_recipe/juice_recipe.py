# Copyright (c) 2026, Your Company
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class JuiceRecipe(Document):
	def validate(self):
		"""Ensure at least one ingredient and validate quantities."""
		if not self.get("ingredients"):
			frappe.throw(
				_("Please add at least one ingredient to the recipe for Item {0}.").format(
					self.item
				)
			)
		for row in self.get("ingredients"):
			if flt(row.quantity_per_unit) <= 0:
				frappe.throw(
					_("Row #{0}: Quantity per unit must be greater than 0 for raw material '{1}'.").format(
						row.idx, row.raw_material
					)
				)
