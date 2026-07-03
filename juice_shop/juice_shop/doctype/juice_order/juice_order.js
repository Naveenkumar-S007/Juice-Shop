// Copyright (c) 2026, Your Company
// License: MIT

frappe.ui.form.on("Juice Order", {
	onload: function (frm) {
		if (frm.is_new() && !frm.doc.order_time) {
			frm.set_value("order_time", frappe.datetime.now_time());
		}
	},
});
