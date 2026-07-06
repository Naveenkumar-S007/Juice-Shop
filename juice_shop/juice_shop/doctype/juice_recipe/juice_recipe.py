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

	def on_update(self):
		"""Sync the Juice Recipe link back to the Item doctype so it's visible.
		Fires on both insert and subsequent saves."""
		try:
			self._sync_to_item()
		except Exception:
			# Custom field may not exist yet — run `bench migrate` to create it
			pass

	def on_trash(self):
		"""Clear the Juice Recipe link on the Item when recipe is deleted."""
		try:
			if frappe.db.exists("Item", self.item):
				frappe.db.set_value("Item", self.item, "custom_juice_recipe", None)
		except Exception:
			pass

	def _sync_to_item(self):
		"""Set custom_juice_recipe field on the linked Item."""
		if frappe.db.exists("Item", self.item):
			frappe.db.set_value("Item", self.item, "custom_juice_recipe", self.name)
