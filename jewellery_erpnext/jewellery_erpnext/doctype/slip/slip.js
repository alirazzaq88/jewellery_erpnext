// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Slip', {
	// refresh: function(frm) {

	// }
	get_operation_cards:function(frm){
		frm.doc.slip_operation_card_detial = []
		let filters = {"docstatus": 1, "purity": frm.doc.purity, "operation": frm.doc.previous_operation}
		frappe.db.get_list("Operation Card", {"filters": filters ,"fields":["name"]}).then((r)=>{
			r.forEach((i) => {
				var a = frappe.model.add_child(cur_frm.doc, "Slip Operation Card Detial", "slip_operation_card_detial");
				 a.operation_card = i.name;
				//  a.description = i.description;
			})
			refresh_field("slip_operation_card_detial"); 
	}
		)
}
});
