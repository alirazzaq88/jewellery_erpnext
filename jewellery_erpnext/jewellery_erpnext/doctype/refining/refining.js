frappe.ui.form.on('Refining', {
	validate(frm) {
		if (!frm.doc.multi_operation) {
			frm.clear_table("refining_operation_details")
			frm.refresh_field("refining_operation_details")
		}
		else {
			frm.set_value("employee", null)
			frm.set_value("operation", null)
		}
	},
	date_from(frm) {
		var today = frappe.datetime.now_date();
		var entered_date = frm.doc.date_from;
		if (entered_date > today) {
			frappe.msgprint("Future dates are not allowed!");
			frm.set_value("date_from", today);
		}
		else if(entered_date > frm.doc.date_to) {
			frappe.msgprint("'Date From' cannot be after 'Date To'");
			frm.set_value("date_from", frm.doc.date_to);
		}
	},
	date_to(frm) {
		var today = frappe.datetime.now_date();
		var entered_date = frm.doc.date_to;
		if (entered_date > today) {
			frappe.msgprint("Future dates are not allowed!");
			frm.set_value("date_to", today);
		}
		else if(entered_date < frm.doc.date_from) {
			frappe.msgprint("'Date To' cannot be before 'Date From'");
			frm.set_value("date_to", frm.doc.date_from);
		}
	},
	refining_gold_weight(frm) {
		frm.trigger("purity")
	},
	purity(frm) {
		if (frm.doc.purity >100 || frm.doc.purity < 0) {
		    frappe.msgprint("Purity must be between 0 to 100")
		    frm.set_value("purity",0)
		}
		let fine_weight = flt(frm.doc.refining_gold_weight) * flt(frm.doc.purity) / 100
		frm.set_value("fine_weight", fine_weight)
	}
});
