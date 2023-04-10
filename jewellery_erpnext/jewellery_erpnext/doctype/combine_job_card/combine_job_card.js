// Copyright (c) 2022, Nirali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Combine Job Card', {
  setup: function (frm) {
    frm.set_query("job_card", "details", function (doc) {
      return {
        "filters": {
          "operation": doc.operation,
          'docstatus': 0,
          'status': 'Open'
        }
      };
    });
    frm.set_query("production_plan", function (doc) {
      return {
        "filters": [
          ['docstatus', '=', 1],
          ['status', 'not in', ['Completed', 'Closed', 'Cancelled']]
        ]
      };
    });
  },
  refresh(frm) {
    if (!frm.doc.__islocal && !frm.doc.details.find(jc=>jc.submitted)) {
      frm.add_custom_button(__("Material Transfer"), () => {
        frm.trigger("make_stock_entry");
      })
      let se_list = frm.doc.details.filter(jc => jc.stock_entry && !jc.submitted).map(ob=>[ob.stock_entry,ob.name])
      if (se_list.length > 0) {
        frm.add_custom_button(__("Submit Material Transfer"), () => {
          frm.call({
            method: "jewellery_erpnext.jewellery_erpnext.doctype.combine_job_card.combine_job_card.submit_stock_entry",
            args: {
              doclist:se_list
            },
            callback: function(r) {
              let res = r.message
              if (res.length > 0) {
                frappe.show_alert({message:__("Something went wrong. Check Error Log"), indicator: 'orange'})
              }
              else frappe.show_alert({message:__("Documents submitted successfully"), indicator: 'green'})
            }
          })
        }).addClass("btn-primary")
      }
    }
  },
  make_stock_entry: function(frm) {
    let jc_list = frm.doc.details.filter(jc => !jc.stock_entry).map(ob=>[ob.job_card,ob.name])
    frappe.call({
      method: "jewellery_erpnext.jewellery_erpnext.doctype.combine_job_card.combine_job_card.create_stock_entry",
      args: {
        job_cards: jc_list
      },
      callback: function(r) {
        let res = r.message
        if (res.length >0)  frappe.msgprint(__("Stock Entries Created: "+res.map(ob=>frappe.utils.get_form_link("Stock Entry",ob,true)).join(", ")))
        else frappe.msgprint("No entries created")
      }
    });
  },
  get_job_cards: function (frm) {
    frappe.call({
      method: "get_job_cards",
      doc: frm.doc,
      callback: function () {
        frm.refresh_field('details');
      }
    })
  },
  add_out_weight: function (frm) {
    var dialog = new frappe.ui.Dialog({
      title: __("Create Out Weight"),
      fields: [
        {
          "fieldtype": "Link", "label": __("Next Operation"), "fieldname": "next_operation",
          "reqd": 1, "options": "Operation",
          onchange: function () {
            frappe.db.get_value("Operation", this.get_value(), 'combine_job_card', function (r) {
              dialog.fields_dict.combine_job_card.set_value(r.combine_job_card || 0)
              if (r.combine_job_card) {
                dialog.set_df_property('to_job_card', 'hidden', 1);
                dialog.set_df_property('to_combine_job_card', 'hidden', 0);
                dialog.set_df_property('to_job_card', 'reqd', 0);
                dialog.set_df_property('to_combine_job_card', 'reqd', 1);
              }
              else {
                dialog.set_df_property('to_job_card', 'hidden', 0);
                dialog.set_df_property('to_combine_job_card', 'hidden', 1);
                dialog.set_df_property('to_job_card', 'reqd', 1);
                dialog.set_df_property('to_combine_job_card', 'reqd', 0);
              }
            })
          }
        },
        {
          "fieldtype": "Check", "label": __("Is Combined operation"), "fieldname": "combine_job_card",
          "read_only": 1,
        },
        {
          "fieldtype": "Link", "label": __("To Combine Job Card"), "fieldname": "to_combine_job_card",
          "reqd": 0, "options": "Combine Job Card",
          get_query: () => { return { filters: { 'operation': dialog.get_value('next_operation'), 'production_plan': frm.doc.production_plan } } },
        },
        {
          "fieldtype": "Link", "label": __("To Job Card"), "fieldname": "to_job_card",
          "reqd": 0, "options": "Job Card", "hidden": 1,
          get_query: () => { return { filters: { "docstatus": 0, 'operation': dialog.get_value('next_operation') } } },
        },
        {
          "fieldtype": "Float", "label": __("Gross Wt"), "fieldname": "gross_wt",
          "reqd": 1,
          onchange: function () {
            let gr = dialog.get_value('gross_wt')
            let purity = dialog.get_value('purity')

            dialog.fields_dict.net_wt.set_value(gr * purity / 100)
          }
        },

        {
          "fieldtype": "Float", "label": __("Purity"), "fieldname": "purity",
          "default": 100,
          onchange: function () {
            let gr = dialog.get_value('gross_wt')
            let purity = dialog.get_value('purity')

            dialog.fields_dict.net_wt.set_value(gr * purity / 100)
          }
        },
        {
          "fieldtype": "Float", "label": __("Net Wt"), "fieldname": "net_wt", "read_only": 1
        },

      ]
    });
    dialog.show();
    dialog.set_primary_action(__("Create"), function () {
      var values = dialog.get_values();
      frappe.call({
        method: "jewellery_erpnext.jewellery_erpnext.doc_events.job_card.create_internal_transfer",
        args: {
          'company': frm.doc.company,
          'from_combine_job_card': frm.doc.name,
          'to_job_card': values.to_job_card,
          'to_combine_job_card': values.to_combine_job_card,
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
  },
});
