// Copyright (c) 2022, satya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Melting Lot', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 0) {
            if(!frm.doc.__islocal && !frm.doc.operation_card){
                frm.add_custom_button(__("Operation Card"), function() {
                    frm.trigger("create_operation_card")
                },("Create")); 
                frm.reload()
            }
            frm.add_custom_button(__('Design Order'), function () {
                // const allowed_request_types = ["Material Transfer", "Material Issue", "Customer Provided"];
                // const depends_on_condition = "eval:doc.material_request_type==='Customer Provided'";
                const d = erpnext.utils.map_current_doc({
                    method: "jewellery_erpnext.jewellery_erpnext.doctype.melting_lot.melting_lot.make_melting_lot",
                    source_doctype: "Design Order",
                    setters: [
                        {
                            fieldtype: 'Link',
                            label: __('Customer'),
                            options: 'Customer',
                            fieldname: 'customer_name',
                            default: frm.doc.customer_name || undefined
                        },

                    ],
                    get_query_filters: {
                        docstatus: 1,
                        // cus
                        // material_request_type: ["in", allowed_request_types],
                        // status: ["not in", ["Transferred", "Issued", "Cancelled", "Stopped"]]
                    }
                })
                setTimeout(() => {
                    // alert(frm.doc.deign_order)
                        if (frm.doc.deign_order !== "undefined"){
                            cur_dialog.wrapper.find('[data-fieldname="search_term"]').val(frm.doc.deign_order)
                            cur_dialog.wrapper.find('[data-fieldname="search_term"]').trigger('change')                       }
                }, 1000)
            }, __("Get Items From"));
        }
        if (frm.doc.operation_card) {
            var wrapper = frm.fields_dict['operation_card'].wrapper
            $(`<a href= /app/operation-card/${frm.doc.operation_card}> View </a>`).appendTo(wrapper);
        }
    },
    create_operation_card(frm) {
		frappe.model.open_mapped_doc({
			method: "jewellery_erpnext.jewellery_erpnext.doctype.operation_card.operation_card.make_operation_card",
			frm: frm
		})
	},
    product_purity: function (frm) {
        calculate_weight(frm)
    },
});

frappe.ui.form.on('Metal Details', {
    in_weight: function (frm, cdt, cdn) {
        calculate_weight(frm)
    },
    purity: function (frm, cdt, cdn) {
        calculate_weight(frm)
    },
    metal_detail_remove: function (frm, cdt, cdn) {
        calculate_weight(frm)
    }
});

frappe.ui.form.on('Melting Lot Design Order Detail', {
    qty: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        doc.production_qty=flt(doc.qty)
        doc.balance_production_qty=flt(doc.qty)-flt(doc.production_qty)
        doc.balance_ready_qty=flt(doc.qty)
        refresh_field("order_details")
    },
    production_qty: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn];
        doc.balance_production_qty=flt(doc.qty)-flt(doc.production_qty)
        refresh_field("order_details")
    },
});


frappe.ui.form.on('Melting Lot Design Order Bunch Detail', {
    length: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        doc.production_length=flt(doc.length)
        doc.balance_production_length=flt(doc.length)-flt(doc.production_length)
        doc.balance_ready_length=flt(doc.length)
        refresh_field("order_bunch_details")
    },
    production_length: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        doc.balance_production_length=flt(doc.length)-flt(doc.production_length)
        refresh_field("order_bunch_details")
    },
    ready_length: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        // doc.balance_production_length=flt(doc.length)-flt(doc.production_length)
    },
    weight: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        doc.production_weight=flt(doc.weight)
        doc.balance_production_weight=flt(doc.weight)-flt(doc.production_weight)
        doc.balance_ready_weight=flt(doc.weight)
        refresh_field("order_bunch_details")
    },
    production_weight: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        doc.balance_production_weight=flt(doc.weight)-flt(doc.production_weight)
        refresh_field("order_bunch_details")
    },
    ready_weight: function (frm, cdt, cdn) {
        var doc=locals[cdt][cdn]
        // doc.balance_production_length=flt(doc.length)-flt(doc.production_length)
    },
    
});

function calculate_weight(frm) {
    var total_fine_weight = 0
    var total_alloy_weight = 0
    if (frm.doc.metal_detail) {
        frm.doc.metal_detail.forEach(function (item) {
            var fine_weight = flt(((item.in_weight) === "undefined" ? 0.0 : item.in_weight)) * parseFloat(((item.purity) === "undefined" ? 0.0 : flt(item.purity) / 100))
            item.fine_weight = flt(fine_weight)
            total_fine_weight += item.fine_weight
            // alert(fine_weight)
            item.alloy_weight = flt(((item.in_weight) === "undefined" ? 0.0 : item.in_weight)) - item.fine_weight
            total_alloy_weight += item.alloy_weight
        })
        frm.set_value("total_fine_weight", total_fine_weight)
        frm.set_value("total_alloy_weight", total_alloy_weight)
        var gross_weight = total_fine_weight / flt(((frm.doc.product_purity) === null ? 0.0 : frm.doc.product_purity)) * 100
        frm.set_value("gross_weight", gross_weight)
        frm.set_value("additional_alloy_weight", gross_weight - total_fine_weight - total_alloy_weight)
        refresh_field("total_fine_weight")
        refresh_field("total_alloy_weight")
        refresh_field("additional_alloy_weight")
        refresh_field("metal_detail")
    }
}