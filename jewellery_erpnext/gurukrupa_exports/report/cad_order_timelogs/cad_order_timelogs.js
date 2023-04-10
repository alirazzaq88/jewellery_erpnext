// Copyright (c) 2023, Nirali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CAD Order TimeLogs"] = {
	"filters": [
		{
			"label": __("CAD Order"),
			"fieldname": "cad_order",
			"fieldtype": "Link",
			"options": "CAD Order"
		},
		{
			"label": __("Workflow State"),
			"fieldname": "workflow_state",
			"fieldtype": "Data"
		},
	]
};
