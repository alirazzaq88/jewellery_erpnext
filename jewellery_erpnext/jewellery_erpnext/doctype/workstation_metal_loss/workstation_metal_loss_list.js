frappe.listview_settings["Workstation Metal Loss"] = {
    onload: function (listview) {
        listview.page.add_menu_item(__("Add Workstations"), function () {
            let d = new frappe.ui.Dialog({
                title: 'Update Workstation Metal Loss',
                fields: [
                    {
                        fieldtype: "Date",
                        fieldname: "from_date",
                        label: "From Date",
                        options: "",
                        defualt: "Today"

                    },
                    {
                        fieldtype: "Date",
                        fieldname: "to_date",
                        label: "To Date",
                        options: "",
                        defualt: "Today"

                    },
                ],
                primary_action_label: 'Update',
                primary_action(values) {
                    frappe.call({
                        method: "jewellery_erpnext.jewellery_erpnext.doc_events.workstation_metal_loss.update_metal_loss",
                        args: {
                            data: values
                        },
                        async: true,
                        type: "POST",
                        callback: function(r) {
                            location.reload()
                            console.log("Success");
                            }
                        })
                
                d.hide();
                // listview.refresh();
                frappe.msgprint('Updated')
                    // frappe.reload_doctype("Attendee")
                    // location.reload()

                }
            })
            d.show();
        });
    },
};