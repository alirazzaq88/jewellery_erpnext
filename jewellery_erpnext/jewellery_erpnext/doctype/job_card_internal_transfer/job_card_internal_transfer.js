// Copyright (c) 2022, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Card Internal Transfer', {
	refresh: function (frm) {
		if (!frm.doc.__islocal && !frm.doc.received) {
			frm.add_custom_button("Received", function () {
				frappe.db.set_value("Job Card Internal Transfer", frm.doc.name, "received", 1).then((res) => {
					frm.reload_doc()
				})
			})
		}
	}
});
