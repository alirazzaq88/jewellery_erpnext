// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Order', {
	// refresh: function(frm) {

	// }
	sales_order_item: function(frm){
		frappe.call({
			method: "jewellery_erpnext.jewellery_erpnext.doctype.production_order.production_order.get_item_code",
			args:{
				'sales_order_item': frm.doc.sales_order_item
			},
			type: "GET",
			callback: function(r) {
				console.log(r.message)
				frm.doc.item_code = r.message
				frm.set_value('item_code', r.message)
				refresh_field('item_code')
				frm.trigger('item_code')
				}
			})
	}
});
