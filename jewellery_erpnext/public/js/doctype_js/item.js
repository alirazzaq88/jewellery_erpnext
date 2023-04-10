frappe.ui.form.on('Item', {
	onload_post_render:function(frm){
    if(frappe.session.user == 'Administrator'){
      frm.set_df_property("is_system_item", "read_only", 0);
    }
    else{
      frm.set_df_property("is_system_item", "read_only", 1);
    }
	},
  setup: function(frm){
    frm.set_query('subcategory', function(doc) {
				return{ filters: {'attribute_type': 'subcategory'}}
		});
  }
})

frappe.ui.form.on('Cad To Finish Weight Estimated Details', {
	cad_weight(frm, cdt,cdn) {
	    var row = locals[cdt][cdn]
	    if (!row.cad_weight) return
		frappe.call({
		    method: "jewellery_erpnext.jewellery_erpnext.doc_events.item.calculate_item_wt_details",
		    args: {
		        doc: row,
		        bom: frm.doc.master_bom,
				item: frm.doc.name
		    },
		    callback:function(r) {
		        console.log(r.message)
		        frappe.model.sync(r.message)
		        frm.refresh()
		    }
		})
	},
	touch(frm,cdt,cdn) {
	    var row = locals[cdt][cdn]
	    console.log(row.touch)
	    if (row.touch == '10KT') {
	        frappe.model.set_value(cdt,cdn,"estimated_finish_gold_wt",row.estimated_10kt_gold_wt)
	    }
	    else if (row.touch == '14KT') {
	        frappe.model.set_value(cdt,cdn,"estimated_finish_gold_wt",row.estimated_14kt_gold_wt)
	    }
	    else if (row.touch == '18KT') {
	        frappe.model.set_value(cdt,cdn,"estimated_finish_gold_wt",row.estimated_18kt_gold_wt)
	    }
	    else if (row.touch == '22KT') {
	        frappe.model.set_value(cdt,cdn,"estimated_finish_gold_wt",row.estimated_22kt_gold_wt)
	    }
	    else if (row.touch == 'Silver') {
	        frappe.model.set_value(cdt,cdn,"estimated_finish_gold_wt",row.estimated_silver_wt)
	    }
	},
	estimated_finish_gold_wt(frm,cdt,cdn) {
	    var row = locals[cdt][cdn]
	    frappe.model.set_value(cdt,cdn,"total_gold_wt",flt(row.estimated_finish_gold_wt) + flt(row.estimated_finding_gold_wt_bom))
	}
})