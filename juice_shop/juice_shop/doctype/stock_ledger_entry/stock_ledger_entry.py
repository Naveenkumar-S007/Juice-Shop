# Copyright (c) 2026, Your Company
# License: MIT
"""Stock Ledger Entry is a simple, append-only audit trail of every raw
material stock movement (consumption from a Juice Order, or a reversal
when that order is cancelled). Entries are written by
raw_material.adjust_stock() and are not meant to be created or edited by
hand."""

from frappe.model.document import Document


class StockLedgerEntry(Document):
	pass
