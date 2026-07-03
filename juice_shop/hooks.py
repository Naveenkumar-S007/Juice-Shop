app_name = "juice_shop"
app_title = "Juice Shop"
app_publisher = "Your Company"
app_description = "Simple juice shop menu, order and daily sales tracking"
app_email = "you@example.com"
app_license = "MIT"
required_apps = ["frappe"]

# Document Events
# ----------------
doc_events = {
	"Juice Order": {
		"on_submit": "juice_shop.juice_shop.doctype.juice_order.juice_order.on_juice_order_submit",
	},
	"Waste Entry": {
		"on_submit": "juice_shop.juice_shop.doctype.waste_entry.waste_entry.on_waste_entry_submit",
	}
}

# Fixtures (optional, export master data with the app)
fixtures = [
	{"doctype": "Juice Item"},
	{"doctype": "Waste Reason"},
	{"doctype": "Raw Material"}
]
