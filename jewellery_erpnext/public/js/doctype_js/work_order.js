frappe.ui.form.on('Work Order', {
	setup: function(frm) {
    frm.set_query("operation", "required_items", function() {
      return {
       // query: "erpnext.manufacturing.doctype.work_order.work_order.get_bom_operations",
        // filters: {
        //   //docstatus: 0
        // }
      };
    });
  },
  refresh: function(frm){
    if(!frm.doc.__islocal){
      frm.add_custom_button(__('Material Request'), function() {
       frappe.call({
        method:"jewellery_erpnext.jewellery_erpnext.doc_events.work_order.create_material_request",
        args:{
          'docname': frm.doc.name
        },
        callback: function(r){
          if(r.message){
            var doclist = frappe.model.sync(r.message);
            frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
          }
        }
       })
      }, __("Create"));
    }
  }
})