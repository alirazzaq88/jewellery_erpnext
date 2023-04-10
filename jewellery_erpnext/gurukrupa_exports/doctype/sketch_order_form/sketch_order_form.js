frappe.ui.form.on('Sketch Order Form', {
    setup: function(frm) {
        set_item_attribute_filters_in_sketch_order_form_detail_fields(frm);
        set_item_attribute_filters_in_sketch_order_form_category(frm);
        set_item_attribute_filters_in_sketch_order_form_setting_type(frm);
        set_item_attribute_filters_in_sketch_order_form_colour_stone(frm);
        set_filter_for_salesman_name(frm);
		frm.set_query('subcategory', 'order_details', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return{
                filters: {
                    'parent_attribute_value' : d.category
                }
            };
        });
		frm.set_query('subcategory', 'category', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return{
                filters: {
                    'parent_attribute_value' : d.category
                }
            };
        });
		frm.set_query('subsetting_type', 'order_details', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return{
                filters: {
                    'parent_attribute_value' : d.setting_type
                }
            };
        });
		frm.set_query("tag__design_id","order_details", function(doc, cdt, cdn) {
			return {
				filters: {
					"is_design_code": 1
				}
			}
		});
		
        let design_fields = [["tag__design_id", "tag_id"], ["reference_design_id", "reference_tagid"]]
        set_filter_for_design_n_serial(frm, design_fields,"category")
        set_filter_for_design_n_serial(frm, [["reference_designid","reference_tagid"]],"order_details")
    },
    
    delivery_date: function(frm){
        validate_dates(frm, frm.doc, "delivery_date")
		set_dates_in_table(frm, "order_details", "delivery_date");
        set_delivery_days_from_delivery_date_and_order_date(frm); 
    },
    
    estimated_duedate: function(frm){
        validate_dates(frm, frm.doc, "estimated_duedate")
        set_dates_in_table(frm, "order_details", "estimated_duedate");
        set_dates_in_table(frm, "category", "estimated_duedate");
    },

    delivery_days: function(frm){ 
        set_delivery_date_from_order_date_and_delivery_days(frm); 
    }, 

    validate: function(frm){ 
        validate_delivery_date_with_order_date(frm);
    },
    
    concept_image: function(frm) {
        refresh_field('image_preview');
    }
});

frappe.ui.form.on("Sketch Order Form Category", {
    category_add: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        row.delivery_date = frm.doc.delivery_date;
        row.estimated_duedate = frm.doc.estimated_duedate
        refresh_field("category");
    },

    delivery_date(frm, cdt,cdn) {
        let doc = locals[cdt][cdn]
        validate_dates(frm, doc, "delivery_date")
    },

    estimated_duedate(frm, cdt,cdn) {
        let doc = locals[cdt][cdn]
        validate_dates(frm, doc, "estimated_duedate")
    },

    setting_type(frm, cdt, cdn) {
        let d = locals[cdt][cdn]
        if (d.setting_type == "Close") {
            frappe.model.set_value(cdt,cdn,{"sub_setting_type":null,"sub_setting_type2":null})
        }
    }
})

frappe.ui.form.on('Sketch Order Form Detail', {
    order_details_add: function(frm, cdt, cdn){
        var row = locals[cdt][cdn];
        row.delivery_date = frm.doc.delivery_date;
        row.estimated_duedate = frm.doc.estimated_duedate
        refresh_field("order_details");
    },
    
	reference_tagid: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		if (!d.reference_designid && d.reference_tagid) {
			frappe.db.get_value("Serial No", d.reference_tagid, "item_code", (r)=> {
				frappe.model.set_value(cdt, cdn, "reference_designid", r.item_code)
			})
		}
	},

    delivery_date(frm, cdt,cdn) {
        let doc = locals[cdt][cdn]
        validate_dates(frm, doc, "delivery_date")
    },

    estimated_duedate(frm, cdt,cdn) {
        let doc = locals[cdt][cdn]
        validate_dates(frm, doc, "estimated_duedate")
    },

    tag__design_id: function(frm) {
        refresh_field("order_details");
    },
    
    design_image: function(frm, cdt, cdn){
        refresh_field("order_details");
    },
    
    sketch_image: function(frm, cdt, cdn){
        refresh_field("order_details");
    },
    
    design_type: function(frm, cdt, cdn){
        var row = locals[cdt][cdn];
        frappe.model.set_value(row.doctype, row.name, 'category','');
        frappe.model.set_value(row.doctype, row.name, 'subcategory','');
        frappe.model.set_value(row.doctype, row.name, 'setting_type','');
        frappe.model.set_value(row.doctype, row.name, 'sub_setting_type','');
        frappe.model.set_value(row.doctype, row.name, 'gold_target','');
        frappe.model.set_value(row.doctype, row.name, 'diamond_target','');
        frappe.model.set_value(row.doctype, row.name, 'product_size','');
        frappe.model.set_value(row.doctype, row.name, '','');
        frappe.model.set_value(row.doctype, row.name, 'reference_tagdesignid','');
        frappe.model.set_value(row.doctype, row.name, 'design_image','');
        frappe.model.set_value(row.doctype, row.name, 'image','');
        frappe.model.set_value(row.doctype, row.name, 'tag__design_id','');
        frappe.model.set_value(row.doctype, row.name, 'item_code','');
    },
    // reference_designid: function(frm, cdt, cdn){
    //     var row = locals[cdt][cdn];
    //     // frappe.msgprint("Hey")
    //     console.log(row.reference_designid)
    //     frappe.db.get_value("Item", row.reference_designid, 'sketch_image', function(p){
    //         frappe.model.set_value(row.doctype, row.name, 'design_image1',p.sketch_image);
    //         refresh_field("design_image1");
    //         refresh_field("image_preview1");
    //     })
        
    // }
});

function set_delivery_days_from_delivery_date_and_order_date(frm){
    frm.set_value('delivery_days', frappe.datetime.get_day_diff(frm.doc.delivery_date, frm.doc.order_date));
}

function set_delivery_date_from_order_date_and_delivery_days(frm){
    frm.set_value('delivery_date', frappe.datetime.add_days(frm.doc.order_date, frm.doc.delivery_days));
}

function validate_delivery_date_with_order_date(frm) {
    if (frm.doc.delivery_date < frm.doc.order_date) {
        frappe.msgprint(__("You can not select past date in Delivery Date"));
        frappe.validated = false;
    }
}

function set_filter_for_salesman_name(frm) {
    frm.set_query("salesman_name", function() {
        return {
            "filters": { "designation": "Sales Person" }
        };
    });
}

function set_item_attribute_filters_in_sketch_order_form_detail_fields(frm) {
    var fields = [  ['category', 'Item Category'],
                    ['subcategory', 'Item Subcategory'],
                    ['setting_type', 'Setting Type'],
                    ['subsetting_type', 'Sub Setting Type'],
                    ['sub_setting_type2', 'Sub Setting Type'],
                    ['gemstone_type1', 'Gemstone Type'],
                    ['gemstone_type2', 'Gemstone Type'],
                    ['gemstone_type3', 'Gemstone Type'],
                    ['gemstone_type4', 'Gemstone Type'],
                    ['gemstone_type5', 'Gemstone Type'],
                    ['gemstone_type6', 'Gemstone Type'],
                    ['gemstone_type7', 'Gemstone Type'],
                    ['gemstone_type8', 'Gemstone Type']
                   
                    ];
    set_filters_on_child_table_fields(frm, fields, 'order_details');
}


function set_item_attribute_filters_in_sketch_order_form_category(frm) {
    var fields = [  ['category', 'Item Category'],
                    ['subcategory', 'Item Subcategory'],
                    ['setting_type', 'Setting Type'],
                    ['sub_setting_type', 'Sub Setting Type'],
                    ['sub_setting_type2', 'Sub Setting Type'],
                    ['gemstone_type1', 'Gemstone Type'],
                    ['gemstone_type2', 'Gemstone Type'],
                    ['gemstone_type3', 'Gemstone Type'],
                    ['gemstone_type4', 'Gemstone Type'],
                    ['gemstone_type5', 'Gemstone Type'],
                    ['gemstone_type6', 'Gemstone Type'],
                    ['gemstone_type7', 'Gemstone Type'],
                    ['gemstone_type8', 'Gemstone Type'],
                    ];
                    
    set_filters_on_child_table_fields(frm, fields, 'category');
}

function set_item_attribute_filters_in_sketch_order_form_setting_type(frm) {
    var fields = [  ['setting_type', 'Setting Type']];
    set_filters_on_child_table_fields(frm, fields, 'setting_type');
}

function set_item_attribute_filters_in_sketch_order_form_colour_stone(frm) {
    var fields = [  ['color_stone', 'Gemstone Type']];
    set_filters_on_child_table_fields(frm, fields, 'colour_stone');
}

//set delivery date in all order detail rows from delivery date in parent doc
function set_delivery_date_in_order_details(frm) {
    $.each(frm.doc.order_details || [], function(i, d) {
        d.delivery_date = frm.doc.delivery_date;
    });
    refresh_field("order_details");
}

function set_dates_in_table(frm, table, fieldname) {
	$.each(frm.doc[table] || [], function(i, d) {
		d[fieldname] = frm.doc[fieldname];
    });
    refresh_field(table);
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

function set_filters_on_child_table_fields_with_parent_attribute_value(frm, fields, child_table) {
    fields.map(function(field){
        frm.set_query(field[0], "order_details", function() {
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': field[1],
                          'parent_attribute_value' : field[2]}
             };
        });
    });
    frm.refresh_field("order_details");
}

function validate_dates(frm, doc, dateField) {
    let order_date = frm.doc.order_date
    if (doc[dateField] < order_date) {
        frappe.model.set_value(doc.doctype, doc.name, dateField, frappe.datetime.add_days(order_date,1))
    }
}

function set_filter_for_design_n_serial(frm, fields, table) {
	fields.map(function (field) {
		frm.set_query(field[0], table, function (doc, cdt, cdn) {
			return {
				filters: {
					"is_design_code": 1
				}
			}
		});
		frm.set_query(field[1], table, function (doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			if (d[field[0]]) {
				return {
					filters: {
						"item_code": d[field[0]]
					}
				}
			}
			return {}
		})
	});
}