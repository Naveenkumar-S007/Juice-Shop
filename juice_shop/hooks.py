app_name = "juice_shop"
app_title = "Juice Shop"
app_publisher = "Your Company"
app_description = "Juice shop with automatic stock deduction via Sales Invoice / POS"
app_email = "you@example.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# Document Events
# ----------------
doc_events = {
	"Sales Invoice": {
		"on_submit": "juice_shop.juice_shop.sales_invoice_hooks.on_sales_invoice_submit",
		"on_cancel": "juice_shop.juice_shop.sales_invoice_hooks.on_sales_invoice_cancel",
	},
	"Waste Entry": {
		"on_submit": "juice_shop.juice_shop.doctype.waste_entry.waste_entry.on_waste_entry_submit",
	}
}

# Fixtures (optional, export master data with the app)
# Note: Raw Material, Juice Recipe, and Waste Reason are shop-specific
# transactional records, not app fixtures.
fixtures = [
	{"doctype": "Waste Reason"}
]
