// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department IR', {
	refresh: function(frm) {
		// Get the value of the "type" field in the parent doctype
		// var parent_type = frm.doc.type;
		// console.log(parent_type)
		// // Iterate over the child table rows and hide the "status" field if the parent type is not "Issue"
		// frm.fields_dict['department_ir_batches'].grid.grid_rows.forEach(function(row) {
		// var status_field = row.fields_dict.status;
		// console.log(status_field)
		// if (parent_type !== 'Issue') {
		// 	status_field.$wrapper.hide();
		// } else {
		// 	status_field.$wrapper.show();
		// }
		// });
	}
});
