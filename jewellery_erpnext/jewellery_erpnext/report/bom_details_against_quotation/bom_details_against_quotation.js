frappe.query_reports["BOM details against Quotation"] = {
        "filters": [
                {
                        "fieldname":"qname",
                        "label": __("name"),
                        "fieldtype": "Link",
                        "options": "Quotation",
                        "reqd":1
                },

        ]
}
