frappe.ui.form.on('Customer', {
	setup: function(frm) {
        var child_fields = [['diamond_quality','Diamond Quality'], 
                            ['diamond_grade_1','Diamond Grade'],
                            ['diamond_grade_2','Diamond Grade'],
                            ['diamond_grade_3','Diamond Grade'],
                            ['diamond_grade_4','Diamond Grade']];
        set_filters_on_child_table_fields(frm, child_fields, "diamond_grades");
        let metal_fields = [['metal_touch','Metal Touch']]
        set_filters_on_child_table_fields(frm, metal_fields, "metal_criteria");
        frm.set_query("metal_purity", "metal_criteria", function(doc, cdt, cdn) {
            var d = locals[cdt][cdn]
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': "Metal Purity", "metal_touch":d.metal_touch}
            }
        })
        
    },
})

function set_filters_on_child_table_fields(frm, fields, table) {
    fields.map(function(field){
        frm.set_query(field[0], table, function() {
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': field[1]}
            }
        })
    })
}

frappe.ui.form.on('Customer', {
	refresh(frm) {
		frm.set_value("vendor_code",frm.doc.name)
	},
	validate(frm) {
	    var purity = []
	    $.each(frm.doc.metal_criteria || [], function(i,d) {
	        if (in_list(purity,d.metal_purity)) {
	            frappe.throw("Metal Purity must be Unique")
	        }
	        else {
	            purity.push(d.metal_purity)
	        }
	    })
	}
})