# Copyright (c) 2026, Your Company
# License: MIT
"""Stock Ledger Entry is an append-only audit trail of every raw material
stock movement. Entries are created automatically when a Juice Order,
Waste Entry, or Stock Adjustment is submitted or cancelled — they are
not meant to be created or edited manually."""

from frappe.model.document import Document


class StockLedgerEntry(Document):
	pass
