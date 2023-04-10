frappe.ui.form.on('Quotation', {
    refresh(frm) {
        frm.add_custom_button(__("CAD Order"), function(){
            erpnext.utils.map_current_doc({
                method: "jewellery_erpnext.gurukrupa_exports.doctype.cad_order.cad_order.make_quotation",
                source_doctype: "CAD Order",
                target: me.frm,
                setters: [
                    {
                        label: "CAD Order Form",
                        fieldname: "cad_order_form",
                        fieldtype: "Link",
                        options: "CAD Order Form"
                    }
                ],
                get_query_filters: {
                    item: ['is', 'set'],
                    docstatus: 1
                }
            })
        }, __("Get Items From"))
    },
    validate: function (frm) {
        frm.doc.items.forEach(function (d) {
            if (d.quotation_bom) {
                frappe.db.get_value("Item Price",
                    { "item_code": d.item_code, "price_list": frm.doc.selling_price_list, "bom_no": d.quotation_bom },
                    'price_list_rate',
                    function (r) {
                        if (r.price_list_rate) {
                            frappe.model.set_value(d.doctype, d.name, 'rate', r.price_list_rate)
                        }
                    })
            }
        })
    },
	setup: function(frm) {
        var parent_fields = [['diamond_quality','Diamond Quality'],
                             ['diamond_grade','Diamond Grade'],
                             ['gemstone_cut_or_cab', 'Cut Or Cab'],
                             ['colour', 'Metal Colour'],
                             ['gemstone_quality', 'Gemstone Quality']];
        set_item_attribute_filters_on_fields_in_parent_doctype(frm, parent_fields);
        set_item_attribute_filters_on_fields_in_child_doctype(frm, parent_fields);
        frm.set_query("diamond_quality", function (doc) {
            var customer = null
            if (doc.quotation_to == "Customer") {
                customer = doc.party_name
            }
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': "Diamond Quality", 'customer_code': customer}
            }
        })
        frm.set_query("diamond_quality", "items", function (doc,cdt,cdn) {
            var customer = null
            if (doc.quotation_to == "Customer") {
                customer = doc.party_name
            }
            return {
                query: 'jewellery_erpnext.query.item_attribute_query',
                filters: {'item_attribute': "Diamond Quality", 'customer_code': customer}
            }
        })
    },
    
    diamond_quality: function(frm) {
		frm.doc.items.filter(item => {
            item.diamond_quality=frm.doc.diamond_quality
            refresh_field('items')
        })
	},
	
	party_name: function(frm){
	    frappe.call({
            method: "jewellery_erpnext.jewellery_erpnext.doc_events.quotation.get_gold_rate",
            args: {
                party_name: frm.doc.party_name,
                currency: frm.doc.currency
            },
            callback: function (r) {
                console.log(r.message)
                frm.doc.gold_rate_with_gst = r.message
            }
        });
	},
	currency: function(frm){
	    frappe.call({
            method: "jewellery_erpnext.jewellery_erpnext.doc_events.quotation.get_gold_rate",
            args: {
                party_name: frm.doc.party_name,
                currency: frm.doc.currency
            },
            callback: function (r) {
                console.log(r.message)
                frm.doc.gold_rate_with_gst = r.message
            }
        });
	}
})

function set_item_attribute_filters_on_fields_in_parent_doctype(frm, fields) {
  fields.map(function(field){
    frm.set_query(field[0], function() {
      return {
        query: 'jewellery_erpnext.query.item_attribute_query',
        filters: {'item_attribute': field[1]}
      }
    })
  })
}

function set_item_attribute_filters_on_fields_in_child_doctype(frm, fields) {
  fields.map(function(field){
    frm.set_query(field[0], 'items', function() {
      return {
        query: 'jewellery_erpnext.query.item_attribute_query',
        filters: {'item_attribute': field[1]}
      }
    })
  })
}

frappe.ui.form.on('Quotation Item', {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        row.quotation_bom = ''
    },
    serial_no(frm, cdt,cdn) {
        var d = locals[cdt][cdn]
        if (d.serial_no) {
            frappe.db.get_value("Serial No", d.serial_no, "item_code", (r)=>{
                frappe.model.set_value(cdt,cdn,"item_code", r.item_code)
            })
        }
    },
    edit_bom: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (frm.doc.__islocal) {
            frappe.throw("Please save document to edit the BOM.")
        }
        if (!row.quotation_bom) {
            frappe.throw("Default BOM not exists for item {}".format(row.item_code))
        }
        // if(row.quotation_bom){
        //   window.open('/app/bom/'+row.quotation_bom)
        // }
        var metal_data = [];
        var diamond_data = [];
        var gemstone_data = []
        var finding_data = []
        // Type	Colour	Purity	Weight in gms	Rate	Amount
        const metal_fields = [
            { fieldtype: 'Data', fieldname: "docname", read_only: 1, hidden: 1 },
            { fieldtype: 'Link', fieldname: "metal_type", label: __('Metal Type'), reqd: 1, columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Type' } } } },
            { fieldtype: 'Link', fieldname: "metal_touch", label: __('Metal Touch'), reqd: 1, columns: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Touch' } } } },
            { fieldtype: 'Link', fieldname: "metal_purity", label: __('Metal Purity'), reqd: 1, columns: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Purity' } } } },
            { fieldtype: 'Link', fieldname: "metal_colour", label: __('Metal Colour'), reqd: 1, columns: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Colour' } } } },
            { fieldtype: 'Column Break', fieldname: 'clb1'},
            { fieldtype: 'Float', fieldname: "quantity", label: __('Weight In Gms'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "rate", label: __('Rate'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "amount", label: __('Amount'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Column Break', fieldname: 'clb2'},
            { fieldtype: 'Float', fieldname: "making_rate", label: __('Making Rate'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "making_amount", label: __('Making Amount'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "wastage_rate", label: __('Wastage Rate'), columns: 1},
            { fieldtype: 'Float', fieldname: "wastage_amount", label: __('Wastage Amount'), columns: 1, in_list_view: 1 },
        ];
        const diamond_fields = [
            { fieldtype: 'Data', fieldname: "docname", read_only: 1, hidden: 1 },
            { fieldtype: 'Link', fieldname: "diamond_type", label: __('Diamond Type'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Diamond Type' } } } },
            { fieldtype: 'Link', fieldname: "stone_shape", label: __('Stone Shape'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Stone Shape' } } } },
            { fieldtype: 'Link', fieldname: "diamond_cut", label: __('Diamond Cut'), columns: 1, reqd: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Stone Shape' } } } },
            { fieldtype: 'Link', fieldname: "quality", label: __('Diamond Quality'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Diamond Quality' } } } },
            { fieldtype: 'Column Break', fieldname: 'clb1'},
            { fieldtype: 'Link', fieldname: "sub_setting_type", label: __('Sub Setting Type'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Sub Setting Type' } } } },
            { fieldtype: 'Link', fieldname: "diamond_sieve_size", label: __('Diamond Sieve Size'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Diamond Sieve Size' } } } },
            { fieldtype: 'Link', fieldname: "sieve_size_range", label: __('Sieve Size Range'), columns: 1, read_only: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Diamond Sieve Size Range' } } } },
            { fieldtype: 'Float', fieldname: "size_in_mm", label: __('Size (in MM)'), columns: 1, in_list_view: 1, read_only: 1},
            { fieldtype: 'Column Break', fieldname: 'clb2'},
            { fieldtype: 'Float', fieldname: "pcs", label: __('Pcs'), reqd: 1, in_list_view: 1, columns: 1 },
            { fieldtype: 'Float', fieldname: "quantity", label: __('Weight In Cts'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "weight_per_pcs", label: __('Weight Per Piece'), read_only: 1, columns: 1},
            { fieldtype: 'Float', fieldname: "total_diamond_rate", label: __('Rate'), columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "diamond_rate_for_specified_quantity", columns: 1, label: __('Amount'), in_list_view: 1 },
        ];
        const gemstone_fields = [
            { fieldtype: 'Data', fieldname: "docname", read_only: 1, hidden: 1 },
            { fieldtype: 'Link', fieldname: "gemstone_type", label: __('Gemstone Type'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Gemstone Type' } } } },
            { fieldtype: 'Link', fieldname: "cut_or_cab", label: __('Cut And Cab'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Cut Or Cab' } } } },
            { fieldtype: 'Link', fieldname: "stone_shape", label: __('Stone Shape'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Stone Shape' } } } },
            { fieldtype: 'Column Break', fieldname: 'clb1'},
            { fieldtype: 'Link', fieldname: "gemstone_quality", label: __('Gemstone Quality'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Gemstone Quality' } } } },
            { fieldtype: 'Link', fieldname: "gemstone_size", label: __('Gemstone Size'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Gemstone Size' } } } },
            { fieldtype: 'Link', fieldname: "sub_setting_type", label: __('Sub Setting Type'), columns: 1, reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Sub Setting Type' } } } },
            { fieldtype: 'Column Break', fieldname: 'clb2'},
            { fieldtype: 'Float', fieldname: "pcs", label: __('Pcs'), columns: 1, reqd: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "quantity", label: __('Weight In Cts'), columns: 1, reqd: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "total_gemstone_rate", columns: 1, label: __('Total Gemstone Rate'), in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "gemstone_rate_for_specified_quantity", columns: 1, label: __('Amount'), in_list_view: 1 },
        ]
        const finding_fields = [
            { fieldtype: 'Data', fieldname: "docname", read_only: 1, hidden: 1 },
            { fieldtype: 'Link', fieldname: "finding_category", columns: 1, label: __('Category'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Finding Category' } } } },
            { fieldtype: 'Link', fieldname: "finding_type", columns: 1, label: __('Type'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Finding Sub-Category' } } } },
            { fieldtype: 'Link', fieldname: "metal_touch", columns: 1, label: __('Metal Touch'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Touch' } } } },
            { fieldtype: 'Link', fieldname: "metal_purity", columns: 1, label: __('Metal Purity'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Purity' } } } },
            { fieldtype: 'Column Break', fieldname: 'clb1'},
            { fieldtype: 'Link', fieldname: "finding_size", columns: 1, label: __('Size'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Finding Size' } } } },
            { fieldtype: 'Link', fieldname: "metal_colour", columns: 1, label: __('Metal Colour'), reqd: 1, in_list_view: 1, options: "Attribute Value", get_query() { return { query: 'jewellery_erpnext.query.item_attribute_query', filters: { 'item_attribute': 'Metal Colour' } } } },
            { fieldtype: 'Float', fieldname: "quantity", columns: 1, label: __('Quantity'), reqd: 1, in_list_view: 1, default: 1 },
            { fieldtype: 'Float', fieldname: "rate", columns: 1, label: __('Rate'), reqd: 1, in_list_view: 1, default: 1 },
            { fieldtype: 'Column Break', fieldname: 'clb2'},
            { fieldtype: 'Float', fieldname: "amount", columns: 1, label: __('Amount'), reqd: 1, in_list_view: 1, default: 1 },
            { fieldtype: 'Float', fieldname: "making_rate", label: __('Making Rate'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "making_amount", label: __('Making Amount'), reqd: 1, columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "wastage_rate", label: __('Wastage Rate'), columns: 1, in_list_view: 1 },
            { fieldtype: 'Float', fieldname: "wastage_amount", label: __('Wastage Amount'), columns: 1, in_list_view: 1 },
        ]

        const dialog = new frappe.ui.Dialog({
            title: __("Update"),
            fields: [
                {
                    fieldname: "metal_detail",
                    fieldtype: "Table",
                    label: "Metal Detail",
                    cannot_add_rows: false,
                    data: metal_data,
                    get_data: () => {
                        return metal_data;
                    },
                    fields: metal_fields
                },
                {
                    fieldname: "diamond_detail",
                    fieldtype: "Table",
                    label: "Diamond Detail",
                    cannot_add_rows: false,
                    data: diamond_data,
                    get_data: () => {
                        return diamond_data;
                    },
                    fields: diamond_fields
                },
                {
                    fieldname: "gemstone_detail",
                    fieldtype: "Table",
                    label: "Gemstone Detail",
                    cannot_add_rows: false,
                    data: gemstone_data,
                    get_data: () => {
                        return gemstone_data;
                    },
                    fields: gemstone_fields
                },
                {
                    fieldname: "finding_detail",
                    fieldtype: "Table",
                    label: "Finding Detail",
                    cannot_add_rows: false,
                    data: finding_data,
                    get_data: () => {
                        return finding_data;
                    },
                    fields: finding_fields
                },
            ],
            primary_action: function () {
                const metal_detail = dialog.get_values()["metal_detail"] || [];
                const diamond_detail = dialog.get_values()["diamond_detail"] || [];
                const gemstone_detail = dialog.get_values()["gemstone_detail"] || [];
                const finding_detail = dialog.get_values()["finding_detail"] || [];

                frappe.call({
                    method: 'jewellery_erpnext.jewellery_erpnext.doc_events.quotation.update_bom_detail',
                    freeze: true,
                    args: {
                        'parent_doctype': "BOM",
                        'parent_doctype_name': row.quotation_bom,
                        'metal_detail': metal_detail,
                        'diamond_detail': diamond_detail,
                        'gemstone_detail': gemstone_detail,
                        'finding_detail': finding_detail,
                    },
                    callback: function (r) {
                        frm.reload_doc();
                    }
                });
                dialog.hide();
                refresh_field("items");
            },
            primary_action_label: __('Update')
        });
        frappe.model.with_doc("BOM", row.quotation_bom, function () {
            var doc = frappe.model.get_doc("BOM", row.quotation_bom)
            $.each(doc.metal_detail, function (index, d) {
                dialog.fields_dict.metal_detail.df.data.push({
                    'docname': d.name,
                    'metal_type': d.metal_type,
                    'metal_touch': d.metal_touch,
                    'metal_purity': d.metal_purity,
                    'metal_colour': d.metal_colour,
                    'amount': d.amount,
                    'rate': d.rate,
                    'quantity': d.quantity,
                    'wastage_rate': d.wastage_rate,
                    'wastage_amount': d.wastage_amount,
                    'making_rate': d.making_rate,
                    'making_amount': d.making_amount
                })
                metal_data = dialog.fields_dict.metal_detail.df.data;
                dialog.fields_dict.metal_detail.grid.refresh();
            })
            $.each(doc.diamond_detail, function (index, d) {
                dialog.fields_dict.diamond_detail.df.data.push({
                    'docname': d.name,
                    'diamond_type': d.diamond_type,
                    'stone_shape': d.stone_shape,
                    'quality': d.quality,
                    'pcs': d.pcs,
                    'diamond_cut': d.diamond_cut,
                    'sub_setting_type': d.sub_setting_type,
                    'diamond_grade': d.diamond_grade,
                    'diamond_sieve_size': d.diamond_sieve_size,
                    'sieve_size_range': d.sieve_size_range,
                    'size_in_mm': d.size_in_mm,
                    'quantity': d.quantity,
                    'weight_per_pcs': d.weight_per_pcs,
                    'total_diamond_rate': d.total_diamond_rate,
                    'diamond_rate_for_specified_quantity': d.diamond_rate_for_specified_quantity
                })
                diamond_data = dialog.fields_dict.diamond_detail.df.data;
                dialog.fields_dict.diamond_detail.grid.refresh();
            })
            $.each(doc.gemstone_detail, function (index, d) {
                dialog.fields_dict.gemstone_detail.df.data.push({
                    'docname': d.name,
                    'gemstone_type': d.gemstone_type,
                    'stone_shape': d.stone_shape,
                    'sub_setting_type': d.sub_setting_type,
                    'cut_or_cab': d.cut_or_cab,
                    'pcs': d.pcs,
                    'gemstone_quality': d.gemstone_quality,
                    'gemstone_grade': d.gemstone_grade,
                    'gemstone_size': d.gemstone_size,
                    'quantity': d.quantity,
                    'total_gemstone_rate': d.total_gemstone_rate,
                    'gemstone_rate_for_specified_quantity': d.gemstone_rate_for_specified_quantity
                })
                gemstone_data = dialog.fields_dict.gemstone_detail.df.data;
                dialog.fields_dict.gemstone_detail.grid.refresh();
            })
            $.each(doc.finding_detail, function (index, d) {
                dialog.fields_dict.finding_detail.df.data.push({
                    'docname': d.name,
                    'finding_category': d.finding_category,
                    'finding_type': d.finding_type,
                    'finding_size': d.finding_size,
                    'metal_touch': d.metal_touch,
                    'metal_purity': d.metal_purity,
                    'amount': d.amount,
                    'rate': d.rate,
                    'metal_colour': d.metal_colour,
                    'quantity': d.quantity,
                    'wastage_rate': d.wastage_rate,
                    'wastage_amount': d.wastage_amount,
                    'making_rate': d.making_rate,
                    'making_amount': d.making_amount
                })
                finding_data = dialog.fields_dict.finding_detail.df.data;
                dialog.fields_dict.finding_detail.grid.refresh();
            })
        })
        dialog.show()
        dialog.$wrapper.find('.modal-dialog').css("max-width", "90%");
    }
})

function humanize(str) {
    var i, frags = str.split('_');
    for (i = 0; i < frags.length; i++) {
        frags[i] = frags[i].charAt(0).toUpperCase() + frags[i].slice(1);
    }
    return frags.join(' ');
}
