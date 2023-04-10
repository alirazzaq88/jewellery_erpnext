# Copyright (c) 2022, Nirali and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns =[
		{
			"label": _("Job Card"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Job Card",
			"width": 130
		},
		{
			"label": _("Job Card Status"),
			"fieldname": "job_card_status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 80
		},
		{
			"label": _("Operation"),
			"fieldname": "operation",
			"fieldtype": "Link",
			"options": "Operation",
			"width": 80
		},
		{
			"label": _("Production Item"),
			"fieldname": "production_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 80,
			"hidden": 1
		},
		{
			"label": _("Metal Purity"),
			"fieldname": "metal_purity",
			"fieldtype": "Data",
			"width": 80
		},
		{
			"label": _("In Gold Weight"),
			"fieldname": "in_gold_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("In Diamond Weight"),
			"fieldname": "in_diamond_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("In Gemstone Weight"),
			"fieldname": "in_gemstone_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("In Finding Weight"),
			"fieldname": "in_finding_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("In Other Weight"),
			"fieldname": "in_other_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Total In Gross Weight"),
			"fieldname": "total_in_gross_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Total In Fine Weight"),
			"fieldname": "total_in_fine_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Out Gross Weight"),
			"fieldname": "out_gross_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Total Out Fine Weight"),
			"fieldname": "total_out_fine_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Loss Gold Weight"),
			"fieldname": "loss_gold_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Loss Diamond Weight"),
			"fieldname": "loss_diamond_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Loss Gemstone Weight"),
			"fieldname": "loss_gemstone_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Total Out Gross Weight"),
			"fieldname": "total_out_gross_weight",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Balance Gross Weight"),
			"fieldname": "balance_gross",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Balance Fine Weight"),
			"fieldname": "balance_fine",
			"fieldtype": "Float",
			"width": 80
		},
	]
	return columns

def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		select name, status as job_card_status, work_order, operation, production_item, metal_purity,
		in_gold_weight, in_diamond_weight, in_gemstone_weight, in_other_weight,
		loss_gold_weight, loss_diamond_weight, loss_gemstone_weight, out_gross_weight,
		total_in_gross_weight, total_in_fine_weight, total_out_gross_weight, total_out_fine_weight,
		balance_gross, balance_fine
		from `tabJob Card` where status != "Cancelled" {conditions}
	""",as_dict= True)
	return data

def get_conditions(filters):
	conditions = ""

	if not filters.get("work_order"):
		frappe.throw("Please select work order.")

	if filters.get("work_order"):
		conditions += " and work_order = '%s'" % filters.get("work_order")
	
	return conditions