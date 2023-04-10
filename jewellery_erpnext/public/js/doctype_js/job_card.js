frappe.ui.form.on('Job Card', {
  refresh: function(frm){
    if(frm.doc.docstatus != 1 && frm.doc.total_in_gross_weight != 0){
    frm.add_custom_button(__("Additional Material Transfer"), () => {
      frappe.model.open_mapped_doc({
        method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.make_additional_stock_entry",
        frm: frm,
        run_link_triggers: true
      });
    });

    if(frm.doc.docstatus != 1 && frm.doc.return_balance > 0)
    {
      frm.add_custom_button(__("Create Stock Return"), () => {
        frappe.model.open_mapped_doc({
          method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.make_stock_return",
          frm: frm,
          run_link_triggers: true
        });
      });
    }
    

  }
  },
  onload: function(frm) {
    var new_arrey = [];
    if (frm.doc.operation) {
        frappe.call({
            'method': "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.set_warehouse",
            args: {
                'operation': frm.doc.operation,
                'company': frm.doc.company
            },
            callback: function(r) {
              if(r.message){
                $.each(r.message, function(idx, data) {
                  new_arrey.push(data.warehouse);
                  if(r.message.length == 1 && frm.doc.wip_warehouse != data.warehouse){
                    frm.set_value('wip_warehouse',data.warehouse)
                  }
               });
               frm.set_query("wip_warehouse", function(frm) {
                  return {
                      filters: [
                          ["Warehouse", "name", "in", new_arrey]
                      ]
                  };
                });
              }
            }

        });
    }
  },
  
  add_out_weight: function(frm){
    var dialog = new frappe.ui.Dialog({
      title: __("Create Out Weight"),
      fields: [
        {
          "fieldtype": "Link", "label": __("From Warehouse"), "fieldname": "from_warehouse",
          "reqd": 1, "options": "Warehouse","default": frm.doc.wip_warehouse, 'read_only': 1,
        },
        {
          "fieldtype": "Link", "label": __("From Job Card"), "fieldname": "from_job_card", 'hidden': 1,
          "reqd": 1, "options": "Job Card","default": frm.doc.name, 'read_only': 1,
        },
        {
          "fieldtype": "Check",
          "label": __("Is last operation"),
          "fieldname": "is_last_operation",
          change: function(){
              if (dialog.fields_dict.is_last_operation.get_value()){
                dialog.set_df_property('to_job_card', 'hidden', 1);
                dialog.set_df_property('to_warehouse', 'hidden', 1);
                dialog.set_df_property('next_operation', 'hidden', 1);
                dialog.set_df_property('create_new_job_card', 'hidden', 1);
                dialog.set_df_property('combine_job_card', 'hidden', 1);
                dialog.set_df_property('to_combine_job_card', 'hidden', 1);
                dialog.set_df_property('to_job_card', 'reqd', 0);
                dialog.set_df_property('to_warehouse', 'reqd', 0);
                dialog.set_df_property('next_operation', 'reqd', 0);
                dialog.set_df_property('to_combine_job_card', 'reqd', 0);
              }
              else{
                dialog.set_df_property('to_job_card', 'hidden', 0);
                dialog.set_df_property('to_warehouse', 'hidden', 0);
                dialog.set_df_property('next_operation', 'hidden', 0);
                dialog.set_df_property('create_new_job_card', 'hidden', 0);
                dialog.set_df_property('combine_job_card', 'hidden', 0);
                dialog.set_df_property('to_combine_job_card', 'hidden', 0);
                dialog.set_df_property('to_job_card', 'reqd', 1);
                dialog.set_df_property('to_warehouse', 'reqd', 1);
                dialog.set_df_property('next_operation', 'reqd', 1);
              }
          }
        },
        {
          "fieldtype": "Link", "label": __("Next Operation"), "fieldname": "next_operation",
          "reqd": 1, "options": "Operation",
          
          onchange: function() {
            frappe.db.get_value("Operation",this.get_value(),'combine_job_card',function(r)
              {dialog.fields_dict.combine_job_card.set_value(r.combine_job_card || 0)
              if(r.combine_job_card){
                dialog.set_df_property('to_job_card', 'hidden', 1);
                dialog.set_df_property('to_warehouse', 'hidden', 1);
                dialog.set_df_property('create_new_job_card', 'hidden', 1);
                dialog.set_df_property('to_combine_job_card', 'hidden', 0);
                dialog.set_df_property('to_job_card', 'reqd', 0);
                dialog.set_df_property('to_warehouse', 'reqd', 0);
                dialog.set_df_property('to_combine_job_card', 'reqd', 1);
              }
              else{
                dialog.set_df_property('to_job_card', 'hidden', 0);
                dialog.set_df_property('to_warehouse', 'hidden', 0);
                dialog.set_df_property('create_new_job_card', 'hidden', 0);
                dialog.set_df_property('to_combine_job_card', 'hidden', 1);
                dialog.set_df_property('to_job_card', 'reqd', 1);
                dialog.set_df_property('to_warehouse', 'reqd', 1);
                dialog.set_df_property('to_combine_job_card', 'reqd', 0);
              }
          })}
        },
        {
          "fieldtype": "Check", "label": __("Is Combined operation"), "fieldname": "combine_job_card", 'hidden': 1,
          "read_only":1,
        },
        {
          "fieldtype": "Link", "label": __("To Combine Job Card"), "fieldname": "to_combine_job_card",
          "reqd": 0, "options": "Combine Job Card",
          get_query: () => {return {filters: {'operation':dialog.get_value('next_operation'),'production_plan':frm.doc.production_plan }}},
        },
        {
          "fieldtype": "Check",
          "label": __("Create New job card"),
          "fieldname": "create_new_job_card",
          "hidden":1,
          change: function(){
              if (dialog.fields_dict.create_new_job_card.get_value()){
                dialog.set_df_property('to_job_card', 'hidden', 1);
                dialog.set_df_property('to_warehouse', 'hidden', 1);
                dialog.set_df_property('to_combine_job_card', 'hidden', 1);
                dialog.set_df_property('to_job_card', 'reqd', 0);
                dialog.set_df_property('to_warehouse', 'reqd', 0);
              }
              else{
                dialog.set_df_property('to_job_card', 'hidden', 0);
                dialog.set_df_property('to_warehouse', 'hidden', 0);
                dialog.set_df_property('to_combine_job_card', 'hidden', 0);
                dialog.set_df_property('to_job_card', 'reqd', 1);
                dialog.set_df_property('to_warehouse', 'reqd', 1);
              }
          }
        },
        {
          "fieldtype": "Link", "label": __("To Job Card"), "fieldname": "to_job_card",
          "reqd": 0, "options": "Job Card","hidden":1,
          get_query: () => {return {filters: { "docstatus": 0,'operation':dialog.get_value('next_operation'),'work_order':frm.doc.work_order }}},
          onchange: function() {
            frappe.db.get_value("Job Card",this.get_value(),'wip_warehouse',function(r){
              if(r.wip_warehouse){dialog.fields_dict.to_warehouse.set_value(r.wip_warehouse || '')}
          })}
        },
        {
          "fieldtype": "Link", "label": __("To Warehouse"), "fieldname": "to_warehouse",
          "reqd": 0, "options": "Warehouse", 'read_only': 1,"hidden":1,
        },
        {
          "fieldtype": "Link", "label": __("Item Code"), "fieldname": "item_code",
          "reqd": 1, "options": "Item",
          "default":frm.doc.item_code,
        },
        {
          "fieldtype": "Float", "label": __("Gross Wt"), "fieldname": "gross_wt",
          "reqd": 1,
          "default":frm.doc.out_gross_weight,
          // onchange: function() {
          //   let gr = dialog.get_value('gross_wt')
          //   let purity = dialog.get_value('purity')

          //   dialog.fields_dict.net_wt.set_value(gr*purity/100)
          // }
        },

        {
          "fieldtype": "Float", "label": __("Purity"), "fieldname": "purity","hidden":1,
          "default":frm.doc.metal_purity,
          // onchange: function() {
          //   let gr = dialog.get_value('gross_wt')
          //   let purity = dialog.get_value('purity')

          //   dialog.fields_dict.net_wt.set_value(purity)
          // }
        },
        {
          "fieldtype": "Float", "label": __("Net Wt"), "fieldname": "net_wt","read_only":1,"hidden":1,
        },
        
      ]
    });
    
    dialog.show();
    var to_job_card = ''
    var to_warehouse = ''
    dialog.set_primary_action(__("Create"), function () {
      var values = dialog.get_values();
          if(!values.to_job_card && values.create_new_job_card){
          frappe.call({
            method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.create_new_job_card",
            args: {
              'company': frm.doc.company,
              'posting_date': frm.doc.posting_date,
              'for_quantity': frm.doc.for_quantity,
              'work_order': frm.doc.work_order,
              'bom_no': frm.doc.bom_no,
              'operation': values.next_operation,
              'workstation': frm.doc.workstation,
              'employee' : frm.doc.employee
            },
            freeze:true,
            callback: function(r){
              if(r.message){
                to_job_card = r.message[0]
                to_warehouse = r.message[1]
                frappe.call({
                  method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.create_internal_transfer",
                  args: {
                    'company': frm.doc.company,
                    'work_order': frm.doc.work_order,
                    'from_job_card': values.from_job_card,
                    'to_job_card': to_job_card,
                    'next_operation': values.next_operation,
                    'item_code': values.item_code,
                    'gross_wt': values.gross_wt,
                    'purity': values.purity || 0,
                    'net_wt': values.net_wt || 0,
                    'balance_gross': frm.doc.balance_gross
                  },
                  freeze:true,
                  callback: function (r) {
                    if (r.message) {
                      frappe.set_route("Form", frm.doc.doctype, r.message[0]);
                      location.reload()
                    }
                  }
                })
              }
            }
          })
        }
        else{
          frappe.call({
            method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.create_internal_transfer",
            args: {
              'company': frm.doc.company,
              'work_order': frm.doc.work_order,
              'from_job_card': values.from_job_card,
              'to_job_card': values.to_job_card,
              'to_combine_job_card': values.to_combine_job_card,
              'next_operation': values.next_operation,
              'item_code': values.item_code,
              'gross_wt': values.gross_wt,
              'purity': values.purity || 0,
              'net_wt': values.net_wt || 0,
              'balance_gross': frm.doc.balance_gross
            },
            callback: function (r) {
              if (r.message) {
                frappe.set_route("Form", frm.doc.doctype, r.message[0]);
                location.reload()
              }
            }
          })
        }
        
      
      dialog.hide();
    });
  },
  add_wastage: function(frm){
    var dialog = new frappe.ui.Dialog({
      title: __("Create Stock Entry"),
      fields: [
        {
          "fieldtype": "Link", "label": __("From Warehouse"), "fieldname": "from_warehouse",
          "reqd": 1, "options": "Warehouse","default": frm.doc.wip_warehouse, 'read_only': 1
        },
        {
          "fieldtype": "Link", "label": __("From Job Card"), "fieldname": "from_job_card",
          "reqd": 1, "options": "Job Card","default": frm.doc.name, 'read_only': 1
        },
        {
          "fieldtype": "Link", "label": __("To Warehouse"), "fieldname": "to_warehouse",
          "reqd": 1, "options": "Warehouse", 'read_only': 0,
          get_query: () => {return {filters: { "company": frm.doc.company }}},
        },
        {
          "fieldtype": "Link", "label": __("Item Code"), "fieldname": "item_code",
          "reqd": 1, "options": "Item",
        },
        {
          "fieldtype": "Float", "label": __("Gross Wt"), "fieldname": "gross_wt",
          "reqd": 1,
        },
        {
          "fieldtype": "Float", "label": __("Purity"), "fieldname": "purity",
        },
        {
          "fieldtype": "Float", "label": __("Net Wt"), "fieldname": "net_wt",
        },
        
      ]
    });
    
    dialog.show();
    
    dialog.set_primary_action(__("Create"), function () {
      var values = dialog.get_values();
      frappe.call({
        method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.create_stock_entry",
        args: {
          'company': frm.doc.company,
          'work_order': frm.doc.work_order,
          'from_warehouse': values.from_warehouse,
          'to_warehouse': values.to_warehouse,
          'from_job_card': values.from_job_card,
          'to_job_card': values.to_job_card,
          'next_operation': values.next_operation,
          'item_code': values.item_code,
          'gross_wt': values.gross_wt,
          'purity': values.purity || 0,
          'net_wt': values.net_wt || 0,

        },
        callback: function (r) {
          if (r.message) {
            frappe.set_route("Form", frm.doc.doctype, r.message[0]);
          }
        }
      })
      dialog.hide();
    });
  }
})