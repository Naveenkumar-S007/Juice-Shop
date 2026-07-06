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
	},
	"Item": {
		"on_update": "juice_shop.juice_shop.sales_invoice_hooks.on_item_update",
	}
}

# Custom Fields
# ----------------
# Add a Juice Recipe link on the standard Item form so users can see
# which recipe is linked to each item. Synced automatically by
# Juice Recipe controller (after_insert / on_update / on_trash).
custom_fields = {
	"Item": [
		{
			"fieldname": "juice_recipe_section",
			"fieldtype": "Section Break",
			"label": "Juice Recipe",
			"insert_after": "description",
			"collapsible": 1,
		},
		{
			"fieldname": "custom_juice_recipe",
			"fieldtype": "Link",
			"label": "Juice Recipe",
			"options": "Juice Recipe",
			"read_only": 1,
			"insert_after": "juice_recipe_section",
			"description": "Auto-populated when ingredients are added below. Click to open the recipe.",
		},
		{
			"fieldname": "recipe_ingredients_section",
			"fieldtype": "Section Break",
			"label": "Recipe Ingredients",
			"insert_after": "custom_juice_recipe",
			"collapsible": 0,
		},
		{
			"fieldname": "recipe_ingredients",
			"fieldtype": "Table",
			"label": "Ingredients",
			"options": "Juice Recipe Item",
			"insert_after": "recipe_ingredients_section",
			"description": "Add raw materials and quantities needed to make one serving of this item. A Juice Recipe will be auto-created on save.",
		},
	]
}

# Fixtures (optional, export master data with the app)
# Note: Raw Material, Juice Recipe, and Waste Reason are shop-specific
# transactional records, not app fixtures.
fixtures = [
	{"doctype": "Waste Reason"}
]
