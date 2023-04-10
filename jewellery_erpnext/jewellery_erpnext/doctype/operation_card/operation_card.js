// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operation Card', {
	refresh: function(frm) {
		if(frm.doc.docstatus != 1)
		{
		  frm.add_custom_button(__("Make Loss Entry"), () => {
			frappe.model.open_mapped_doc({
			  method: "jewellery_erpnext.jewellery_erpnext.doctype.operation_card.operation_card.make_stock_return",
			  frm: frm,
			  run_link_triggers: true
			});
		  });
		}
	},

	transfer_stock: function(frm){
		var dialog = new frappe.ui.Dialog({
		  title: __("Create Out Weight"),
		  fields: [
			{
			  "fieldtype": "Link", "label": __("Operation Card"), "fieldname": "operation_card",
			  "reqd": 1, "options": "Operation Card","default":frm.doc.name,  get_query: () => {return {filters: { "production_order": frm.doc.production_order }}},
			},
			{
			  "fieldtype": "Link", "label": __("Operation"), "fieldname": "operation",
			  "reqd": 1, "options": "Operation"
			},
		  ]
		});
		
		dialog.show();
		dialog.set_primary_action(__("Create"), function () {
		  var values = dialog.get_values();
		  frappe.call({
			method: "jewellery_erpnext.jewellery_erpnext.doctype.operation_card.operation_card.make_operation_card_transfer",
			args: {
			  'operation': values.operation,
			  'operation_card': values.operation_card
			},
			freeze:true,
			callback: function (r) {
			  if (r.message) {
				frappe.set_route("Form", frm.doc.doctype, r.message[0]);
				location.reload()
			  }
			}
		  })
		  dialog.hide();
		});
	  },
});
