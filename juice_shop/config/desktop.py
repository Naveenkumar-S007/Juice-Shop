from frappe import _


def get_data():
	return [
		{
			"module_name": "Juice Shop",
			"category": "Modules",
			"label": _("Juice Shop"),
			"color": "orange",
			"icon": "octicon octicon-package",
			"type": "module",
			"description": "Juice menu, orders and daily sales tracking.",
		}
	]
