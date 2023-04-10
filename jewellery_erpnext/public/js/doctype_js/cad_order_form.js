frappe.ui.form.on('CAD Order Form', {
  delivery_date: function(frm) {
      $.each(frm.doc.order_details || [], function(i, d) {
    d.delivery_date = frm.doc.delivery_date;
  });
  refresh_field("order_details");
  },
  setup: function(frm) {
      var fields = [['subcategory', 'Subcategory'], 
              ['purity', 'Metal Purity'], 
              ['setting_type', 'Setting Type'], 
              ['diamond_quality', 'Diamond Quality']];
      set_filters_on_child_table_fields(frm, fields);
      
      var parent_fields = [['diamond_quality','Diamond Quality']];
      set_item_attribute_filters_on_fields_in_parent_doctype(frm, parent_fields);
  },
  
  design_by: function(frm) { set_order_type_from_design_by(frm); },
  
  scan_tag_no: function(frm){
    if(frm.doc.scan_tag_no){
      frappe.call({
        method: "erpnext.selling.page.point_of_sale.point_of_sale.search_for_serial_or_batch_or_barcode_number",
        args:{
          'search_value': frm.doc.scan_tag_no
        },
        callback: function(r){
          if(r.message.item_code){
              let d = frm.add_child('order_details')
              d.tag_no = frm.doc.scan_tag_no
              d.item = r.message.item_code
              d.delivery_date = frm.doc.delivery_date
              d.diamond_quality = frm.doc.diamond_quality
                frappe.model.with_doc("Item", r.message.item_code, function(m) {
          var doc = frappe.model.get_doc("Item", r.message.item_code);
          if(doc.attributes){
              $.each(doc.attributes, function(index, row){
                  var df = frappe.meta.get_docfield(d.doctype,row.attribute.toLowerCase().replace(/\s+/g, '_'), d.name);
                  // console.log(row.attribute)
                  // console.log(df)
                        if(df){df.hidden = 0}
                  var filed = row.attribute.toLowerCase().replace(/\s+/g, '_')
              d[filed]= row.attribute_value
            })
            cur_frm.refresh_field("order_details")
            
          }
        });
            
           
            frm.set_value('scan_tag_no','')
          }
          else{
            frappe.msgprint('Cannot find Item with this barcode')
          }
          frm.refresh_field('order_details')
        }
      })
    }
}
})

frappe.ui.form.on('CAD Order Form Detail', {
  subcategory: function(frm, cdt, cdn){
      hide_all_subcategory_attribute_fields(frm, cdt, cdn);
      
      let order_detail = locals[cdt][cdn];
      show_attribute_fields_for_subcategory(frm, cdt, cdn, order_detail);
  },
  order_details_add:function(frm, cdt, cdn){
      var row = locals[cdt][cdn];
      row.delivery_date = frm.doc.delivery_date;
      refresh_field("order_details");
  }
})

//public function to set item attribute filters on parent doctype
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

//public function to set item attribute filters on child doctype
function set_filters_on_child_table_fields(frm, fields) {
fields.map(function(field){
  frm.set_query(field[0], "order_details", function() {
    return {
      query: 'jewellery_erpnext.query.item_attribute_query',
      filters: {'item_attribute': field[1]}
    }
  })
})
}

//public function to set order type 
function set_order_type_from_design_by(frm) {
  if (cur_frm.doc.design_by=="Customer Design")
      cur_frm.doc.order_type="Customer Order";
  else
      cur_frm.doc.order_type="Stock Order";
  cur_frm.refresh_field("order_type");
}

//public function to hide all item attribute fields
function hide_all_subcategory_attribute_fields(frm, cdt, cdn) {
  var subcategory_attribute_fields = ['Gold Target','Diamond Target','Metal Colour','Product Size','Length','Height','Breadth','Stone Type','Enamal','Rhodium','Gemstone Type','Gemstone Quality','Stone Changeable','Hinges','Back Belt Patti','Back Belt Length','Vanki Type','Black Beed','Black Beed Line','Screw Type','Hook Type','lock Type','2 in 1','Round Kadi','Chain Type','Customer Chain', 'Customer Sample', 'Certificate Place'];
  show_hide_fields(frm, cdt, cdn, subcategory_attribute_fields, 1);
}

//public function to show item attribute fields based on the selected subcategory
function show_attribute_fields_for_subcategory(frm, cdt, cdn, order_detail) {
  if (order_detail.subcategory){
      frappe.model.with_doc("Attribute Value", order_detail.subcategory, function(r) {
    var subcategory_attribute_value = frappe.model.get_doc("Attribute Value", order_detail.subcategory);
    if (subcategory_attribute_value.item_attributes){
        $.each(subcategory_attribute_value.item_attributes, function(index, row){
        show_field(frm, cdt, cdn, row.item_attribute);
          });
    }
  });
  }
}

//private function to show single child table field
function show_field(frm, cdt, cdn, field_name) {
  show_hide_field(frm, cdt, cdn, field_name, 0);
}

//private function to show or hide multiple child table fields
function show_hide_fields(frm, cdt, cdn, fields, hidden){
  fields.map(function(field){
      show_hide_field(frm, cdt, cdn, field, hidden);
  })
}

//private function to show or hide single child table fields
function show_hide_field(frm, cdt, cdn, field, hidden){
  var df = frappe.meta.get_docfield(cdt, field.toLowerCase().replace(/\s+/g, '_'), cdn);
  if (df) { 
      df.hidden = hidden;
      if (df.hidden===0) df.reqd = 1;
  }
  cur_frm.refresh_field("order_details");
}