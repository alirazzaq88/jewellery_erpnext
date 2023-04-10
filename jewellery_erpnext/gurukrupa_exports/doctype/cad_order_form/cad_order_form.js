frappe.ui.form.on('CAD Order Form', {
	delivery_date: function (frm) {
		validate_dates(frm, frm.doc, "delivery_date")
		update_fields_in_child_table(frm, "delivery_date")
		calculate_due_days(frm);
	},
	estimated_duedate(frm) {
		validate_dates(frm, frm.doc, "estimated_duedate")
		update_fields_in_child_table(frm, "estimated_duedate")
	},
	system_due_date(frm) {
		validate_dates(frm, frm.doc, "system_due_date")
	},
	branch(frm) {
		update_fields_in_child_table(frm, "branch")
	},
	project(frm) {
		update_fields_in_child_table(frm, "project")
	},
	setup: function (frm, cdt, cdn) {
		var parent_fields = [['diamond_quality', 'Diamond Quality']];
		set_filters_on_parent_table_fields(frm, parent_fields);

		var fields = [['category', 'Item Category'],
		['subcategory', 'Item Subcategory'],
		['setting_type', 'Setting Type'],
		['purity', 'Metal Purity'],
		['diamond_quality', 'Diamond Quality'],
		['metal_touch', 'Metal Touch'],
		['metal_colour', 'Metal Colour'],
		['sizer_type', 'Sizer Type'],
		['enamal', 'Enamal'],
		['rhodium', 'Rhodium'],
		['gemstone_type', 'Gemstone Type'],
		['gemstone_quality', 'Gemstone Quality'],
		['stone_changeable', 'Stone Changeable'],
		['hinges', 'Hinges'],
		['back_belt_patti', 'Back Belt'],
		['vanki_type', 'Vanki Type'],
		['black_beed', 'Black Beed'],
		['screw_type', 'Screw Type'],
		['hook_type', 'Hook Type'],
		['lock_type', 'Lock Type'],
		['2_in_1', '2 in 1'],
		['kadi_type', 'Kadi Type'],
		['chain', 'Chain'],
		['chain_type', 'Chain Type'],
		['customer_chain', 'Customer Chain'],
		['detachable', 'Detachable'],
		['back_chain', 'Back Chain'],
		['nakshi_from', 'Nakshi From'],
		['nakshi', 'Nakshi'],
		['customer_sample', 'Customer Sample'],
		['certificate_place', 'Certificate Place'],
		['breadth', 'Breadth'],
		['width', 'Width'],
		['back_belt', 'Back Belt'],
		['back_belt_length', 'Back Belt Length'],
		['gemstone_types1', 'Gemstone Type'],
		['gemstone_types2', 'Gemstone Type'],
		['gemstone_types3', 'Gemstone Type'],
		['gemstone_types4', 'Gemstone Type'],
		['gemstone_types5', 'Gemstone Type'],
		['gemstone_types6', 'Gemstone Type'],
		['gemstone_types7', 'Gemstone Type'],
		['gemstone_types8', 'Gemstone Type'],
		['sub_setting_type1', 'Sub Setting Type'],
		['sub_setting_type2', 'Sub Setting Type'],
		['gemstone_quality', 'Gemstone Quality'],
		];

		set_filters_on_child_table_fields(frm, fields);
		set_filter_for_salesman_name(frm);

		let design_fields = [["design_id", "tag_no"], ["reference_designid", "reference_serial_no_1"],
		["reference_design_id_2", "reference_serial_no_2"], ["reference_design_id_3", "reference_serial_no_3"]]
		set_filter_for_design_n_serial(frm, design_fields)
		frm.set_query("parcel_place", function (doc) {
			return {
				query: "jewellery_erpnext.query.get_parcel_place",
				filters: {
					"customer_code": doc.customer_code
				}
			}
		})

		frm.set_query('subcategory', 'order_details', function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: {
					'parent_attribute_value': d.category
				}
			};
		});
		frm.set_query('diamond_quality','order_details', function (doc) {
			return {
				query: 'jewellery_erpnext.query.item_attribute_query',
				filters: { 'item_attribute': "Diamond Quality", "customer_code": doc.customer_code }
			};
		});
		if (frm.doc.order_details) {
			frm.doc.order_details.forEach(function (d) {
				show_attribute_fields_for_subcategory(frm, d.doctype, d.name, d);
			})
		}
	},

	due_days: function (frm) {
		delivery_date(frm);
	},

	validate: function (frm) {
		if (frm.doc.delivery_date < frm.doc.order_date) {
			frappe.msgprint(__("You can not select past date in Delivery Date"));
			frappe.validated = false;
		}
	},

	concept_image: function (frm) {
		refresh_field('image_preview');
	},

	design_by: function (frm) { set_order_type_from_design_by(frm); },

	customer_code: function(frm){
        frm.doc.service_type = [];
        if(frm.doc.customer_code){
         frappe.model.with_doc("Customer", frm.doc.customer_code, function() {
          let customer_doc = frappe.model.get_doc("Customer", frm.doc.customer_code);
          $.each(customer_doc.service_type, function(index, row){
            let d = frm.add_child("service_type");
            d.service_type1 = row.service_type1;
          });
           refresh_field("service_type");
         });
        }
   },

	scan_tag_no: function (frm) {
		if (frm.doc.scan_tag_no) {
			frappe.call({
				method: "erpnext.selling.page.point_of_sale.point_of_sale.search_for_serial_or_batch_or_barcode_number",
				args: {
					'search_value': frm.doc.scan_tag_no
				},
				callback: function (r) {
					if (r.message.item_code) {
						let d = frm.add_child('order_details');
						d.tag_no = frm.doc.scan_tag_no;
						d.item = r.message.item_code;
						d.delivery_date = frm.doc.delivery_date;
						d.diamond_quality = frm.doc.diamond_quality;
						frappe.model.with_doc("Item", r.message.item_code, function (m) {
							var doc = frappe.model.get_doc("Item", r.message.item_code);
							if (doc.attributes) {
								$.each(doc.attributes, function (index, row) {
									var df = frappe.meta.get_docfield(d.doctype, row.attribute.toLowerCase().replace(/\s+/g, '_'), d.name);
									if (df) { df.hidden = 0 }
									var filed = row.attribute.toLowerCase().replace(/\s+/g, '_');
									d[filed] = row.attribute_value;
								});
								cur_frm.refresh_field("order_details");
							}
						});
						frm.set_value('scan_tag_no', '');
					} else {
						frappe.msgprint('Cannot find Item with this barcode');
					}
					frm.refresh_field('order_details');
				}
			});
		}
	}
});

frappe.ui.form.on('CAD Order Form Detail', {
	form_render(frm, cdt, cdn) {
		let order_detail = locals[cdt][cdn];
		if (order_detail.subcategory) {
			set_field_visibility(frm, cdt, cdn)
		}
	},

	tag_no(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		fetch_item_from_serial(d, "tag_no", "design_id")
		if (d.tag_no) {
			frappe.db.get_value("BOM",{"tag_no": d.tag_no},'name', (r)=>{
				frappe.model.set_value(cdt, cdn, 'bom', r.name)
			})
		}
	},

	reference_serial_no_1(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		fetch_item_from_serial(d, "reference_serial_no_1", "reference_designid")
	},

	reference_serial_no_2(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		fetch_item_from_serial(d, "reference_serial_no_2", "reference_design_id_2")
	},

	reference_serial_no_3(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		fetch_item_from_serial(d, "reference_serial_no_3", "reference_design_id_3")
	},

	design_id: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.design_id) {
			frappe.db.get_value("Item", { "name": d.design_id }, ["image", "item_category", "item_subcategory", "setting_type", "master_bom"], function (value) {
				d.design_image = value.image;
				d.image = value.image;
				d.category = value.item_category;
				d.subcategory = value.item_subcategory;
				d.setting_type = value.setting_type;
				set_field_visibility(frm, cdt, cdn)
				refresh_field('order_details');
			});
		} else {
			d.design_image = "";
			d.image = "";
			d.category = "";
			d.subcategory = "";
			d.setting_type = "";
			d.bom = "";
			refresh_field('order_details');
		}
	},

	subcategory: function (frm, cdt, cdn) {
		set_field_visibility(frm, cdt, cdn)
	},

	order_details_add: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.delivery_date = frm.doc.delivery_date;
		row.diamond_quality = frm.doc.diamond_quality;
		row.estimated_duedate = frm.doc.estimated_duedate;
		row.branch = frm.doc.branch
		row.project = frm.doc.project
		refresh_field("order_details");
	},

	design_image: function (frm, cdt, cdn) {
		refresh_field("order_details");
	},

	design_type: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'category', '');
		frappe.model.set_value(row.doctype, row.name, 'subcategory', '');
		frappe.model.set_value(row.doctype, row.name, 'setting_type', '');
		frappe.model.set_value(row.doctype, row.name, 'purity', '');
		frappe.model.set_value(row.doctype, row.name, 'gemstone_price', '');
		frappe.model.set_value(row.doctype, row.name, 'reference_tagdesignid', '');
		frappe.model.set_value(row.doctype, row.name, 'design_image', '');
		frappe.model.set_value(row.doctype, row.name, 'image', '');
		frappe.model.set_value(row.doctype, row.name, 'tag_no', '');
		frappe.model.set_value(row.doctype, row.name, 'item', '');
		frappe.model.set_value(row.doctype, row.name, 'bom', '');
		frappe.model.set_value(row.doctype, row.name, 'design_id', '');
	},

	design_by: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.design_by == "Customer Design") {
			frappe.model.set_value(row.doctype, row.name, 'design_type', 'New Design');
		} else {
			frappe.model.set_value(row.doctype, row.name, 'design_type', '');
		}
	},

	category: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'subcategory', '');
	}
});

function validate_dates(frm, doc, dateField) {
    let order_date = frm.doc.order_date
    if (doc[dateField] < order_date) {
        frappe.model.set_value(doc.doctype, doc.name, dateField, frappe.datetime.add_days(order_date,1))
    }
}

function fetch_item_from_serial(doc, fieldname, itemfield) {
	if (doc[fieldname]) {
		frappe.db.get_value("Serial No", doc[fieldname], 'item_code', (r) => {
			frappe.model.set_value(doc.doctype, doc.name, itemfield, r.item_code)
		})
	}
}

function set_field_visibility(frm, cdt, cdn) {
	hide_all_subcategory_attribute_fields(frm, cdt, cdn);
	var order_detail = locals[cdt][cdn];
	show_attribute_fields_for_subcategory(frm, cdt, cdn, order_detail);
};

//public function to set item attribute filters on child doctype
function set_filters_on_child_table_fields(frm, fields) {
	fields.map(function (field) {
		frm.set_query(field[0], "order_details", function () {
			return {
				query: 'jewellery_erpnext.query.item_attribute_query',
				filters: { 'item_attribute': field[1] }
			};
		});
	});
}

//public function to set item attribute filters on parent doctype
function set_filters_on_parent_table_fields(frm, fields) {
	fields.map(function (field) {
		frm.set_query(field[0], function (doc) {
			return {
				query: 'jewellery_erpnext.query.item_attribute_query',
				filters: { 'item_attribute': field[1], "customer_code": doc.customer_code }
			};
		});
	});
}

//public function to set order type 
function set_order_type_from_design_by(frm) {
	if (cur_frm.doc.design_by == "Customer Design")
		cur_frm.doc.order_type = "Customer Order";
	else
		cur_frm.doc.order_type = "Stock Order";
	cur_frm.refresh_field("order_type");
}

//public function to show item attribute fields based on the selected subcategory
function show_attribute_fields_for_subcategory(frm, cdt, cdn, order_detail) {
	if (order_detail.subcategory) {
		frappe.model.with_doc("Attribute Value", order_detail.subcategory, function (r) {
			var subcategory_attribute_value = frappe.model.get_doc("Attribute Value", order_detail.subcategory);
			if (subcategory_attribute_value.is_subcategory == 1) {
				if (subcategory_attribute_value.item_attributes) {
					$.each(subcategory_attribute_value.item_attributes, function (index, row) {
						if (row.in_cad == 1)
							show_field(frm, cdt, cdn, row.item_attribute);
					});
				}
			}
		});
	}
}

//private function to hide all subcategory related fields in order details
function hide_all_subcategory_attribute_fields(frm, cdt, cdn) {
	var subcategory_attribute_fields = ['Gold Target', 'Diamond Target', 
	'Metal Colour', 'Product Size', 'Length', 'Height', 'Sizer Type', 
	'Enamal', 'Rhodium', 'Stone Type', 'Gemstone Type', 'Gemstone Quality',
	'Stone Changeable', 'Changeable', 'Hinges', 'Back Belt', 'Vanki Type',
	'Black Beed', 'Black Beed Line', 'Screw Type', 'Hook Type', 'Lock Type',
	'2 in 1', 'Kadi Type', 'Chain', 'Chain Type', 'Customer Chain', 'Chain Length',
	'Total Length', 'Chain Weight', 'Detachable', 'Back Chain', 'Back Chain Size',
	'Back Side Size', 'Chain Thickness', 'Total Mugappu', 'Kadi to Mugappu',
	'Space between Mugappu', 'Nakshi', 'Nakshi From', 'Customer Sample',
	'Certificate Place', 'Breadth', 'Width', 'Back Belt', 'Back Belt Length'];
	show_hide_fields(frm, cdt, cdn, subcategory_attribute_fields, 1);
}

//private function to show single child table field
function show_field(frm, cdt, cdn, field_name) {
	show_hide_field(frm, cdt, cdn, field_name, 0);
}

//private function to show or hide multiple child table fields
function show_hide_fields(frm, cdt, cdn, fields, hidden) {
	fields.map(function (field) {
		show_hide_field(frm, cdt, cdn, field, hidden);
	});
}

//private function to show or hide single child table fields
function show_hide_field(frm, cdt, cdn, field, hidden) {
	// var df = frappe.meta.get_docfield(cdt, field.toLowerCase().replace(/\s+/g, '_'), cdn);
	// if (df) {
	//     //console.log(field.toLowerCase().replace(/\s+/g, '_'));
	//     //console.log(df.hidden);
	//     df.hidden = hidden;
	//    // console.log(df.hidden);
	//     if (df.hidden===0) df.reqd = 0;
	// }
	var field_name = field.toLowerCase().replace(/\s+/g, '_')
	var df = frappe.utils.filter_dict(cur_frm.fields_dict["order_details"].grid.grid_rows_by_docname[cdn].docfields, { "fieldname": field_name })[0];
	if (df) {
		df.hidden = hidden;
		if (df.hidden == 0) df.reqd = 0;
	}
	frm.refresh_field("order_details");
}

// Auto calculate due days from delivery date    
function calculate_due_days(frm) {
	frm.set_value('due_days', frappe.datetime.get_day_diff(frm.doc.delivery_date, frm.doc.order_date));
}

// Auto Calculate delivery date from due days
function delivery_date(frm) {
	frm.set_value('delivery_date', frappe.datetime.add_days(frm.doc.order_date, frm.doc.due_days));
}

function set_filter_for_salesman_name(frm) {
	frm.set_query("salesman_name", function () {
		return {
			"filters": { "designation": "Sales Person" }
		};
	});
}

function update_fields_in_child_table(frm, fieldname) {
	$.each(frm.doc.order_details || [], function (i, d) {
		d[fieldname] = frm.doc[fieldname];
	});
	refresh_field("order_details");
}

function set_filter_for_design_n_serial(frm, fields) {
	fields.map(function (field) {
		frm.set_query(field[0], "order_details", function (doc, cdt, cdn) {
			return {
				filters: {
					"is_design_code": 1
				}
			}
		});
		frm.set_query(field[1], "order_details", function (doc, cdt, cdn) {
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