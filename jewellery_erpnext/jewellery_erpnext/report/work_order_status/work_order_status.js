// Copyright (c) 2022, Nirali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Status"] = {
	"filters": [
		{
			fieldname: "work_order",
			label: __("Work Order"),
			fieldtype: "Link",
			options: "Work Order",
			reqd: 1
		},
	]
};
