// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Making Charge Price', {
	setup: function(frm) {
        var parent_fields = [['setting_type','Setting Type'],
                             ['making_charge_type','Making Charge Type'],
                             ['metal_touch','Metal Touch']];
        set_item_attribute_filters_on_fields_in_parent_doctype(frm, parent_fields);
        
        var child_fields = [['subcategory','Item Subcategory']];
        set_filters_on_child_table_fields(frm, child_fields, 'subcategory');
		
		frm.set_query("metal_purity", function(doc) {
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': "Metal Purity", "metal_touch":doc.metal_touch}
            }
        })
    }
});

function set_item_attribute_filters_on_fields_in_parent_doctype(frm, fields) {
  fields.map(function(field){
    frm.set_query(field[0], function() {
      return {
        query: 'jewellery_erpnext.query.item_attribute_query',
        filters: {'item_attribute': field[1]}
      };
    });
  });
}

function set_filters_on_child_table_fields(frm, fields, child_table) {
    fields.map(function(field){
        frm.set_query(field[0], child_table, function() {
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': field[1]}
            };
        });
    });
}