frappe.ui.form.on('Sales Order', {
  refresh: function(frm){
    console.log(frm.doc.docstatus)
    if(frm.doc.docstatus==1){
      frm.add_custom_button(__("Create Production Order"), () => {
        frappe.call({
          'method': "jewellery_erpnext.jewellery_erpnext.doctype.production_order.production_order.make_production_order",
          args: {
            sales_order: frm.doc.name
          },
          callback: function(r) {
            if(r.message){
              console.log("Message")
            }}
      });
    })
  }
  },
  validate:function(frm){
    frm.doc.items.forEach(function(d){
      if(d.bom){
        frappe.db.get_value("Item Price",{"item_code":d.item_code,"price_list":frm.doc.selling_price_list,"bom_no":d.bom},'price_list_rate',function(r){
          if(r.price_list_rate){
            frappe.model.set_value(d.doctype, d.name, 'rate',r.price_list_rate)
          }
        })
      }
    })
  },
})