frappe.ui.form.on('Stock Entry', {
  setup: function(frm){
    frm.set_query('item_template', function(doc) {
			return{ filters: {'has_variants': 1}}
		});
    frm.fields_dict['item_template_attribute'].grid.get_field('attribute_value').get_query = function(frm, cdt, cdn) {
			var child = locals[cdt][cdn];
			return { 
        query: 'jewellery_erpnext.query.item_attribute_query',
        filters: {'item_attribute':child.item_attribute}
      }
		}
  },
  onload_post_render: function(frm){
    frm.fields_dict['item_template_attribute'].grid.wrapper.find('.grid-remove-rows').remove();
    frm.fields_dict['item_template_attribute'].grid.wrapper.find('.grid-add-multiple-rows').remove();
    frm.fields_dict['item_template_attribute'].grid.wrapper.find('.grid-add-row').remove();
  },
  from_job_card: function(frm) {
    $.each(frm.doc.items || [], function(i, d) {
			d.from_job_card = frm.doc.from_job_card;
		});
	},
  to_job_card: function(frm) {
    $.each(frm.doc.items || [], function(i, d) {
			d.to_job_card = frm.doc.to_job_card;
		});
	},
  item_template: function(frm){
    if(frm.doc.item_template){
      frm.doc.item_template_attribute = []
      frappe.model.with_doc("Item", frm.doc.item_template, function() {
				var item_template = frappe.model.get_doc("Item", frm.doc.item_template);
				$.each(item_template.attributes, function(index, d) {
          let row = frm.add_child('item_template_attribute')
          row.item_attribute = d.attribute
       })
       frm.refresh_field('item_template_attribute')
      })
    }
  },
  add_item: function(frm){
    if(!frm.doc.item_template_attribute || !frm.doc.item_template){
      frappe.throw("Please select Item Template.")
    }
    frappe.call({
      method: "jewellery_erpnext.utils.set_items_from_attribute",
      args:{
        item_template: frm.doc.item_template,
        item_template_attribute: frm.doc.item_template_attribute
      },
      callback: function(r){
        if(r.message){
          let item = frm.add_child('items')
          item.item_code = r.message.name
          item.qty = 1
          item.transfer_qty = 1
          item.uom = r.message.stock_uom
          item.stock_uom = r.message.stock_uom
          item.conversion_factor = 1
          frm.refresh_field('items')
          frm.set_value('item_template', '')
          frm.doc.item_template_attribute = []
          frm.refresh_field('item_template_attribute')
        }
      }
    })
  }
})
frappe.ui.form.on("Stock Entry Detail", {
  items_add:function(frm, cdt, cdn){
    var row = locals[cdt][cdn];
    row.from_job_card = frm.doc.from_job_card;
    row.to_job_card = frm.doc.to_job_card;
    refresh_field("items");
  }
})
