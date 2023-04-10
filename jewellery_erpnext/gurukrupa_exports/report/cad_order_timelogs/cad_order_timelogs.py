# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_data(filters):
	condition = get_conditions(filters)
	data = frappe.db.sql(f"""select completed_by, status, reference_name, creation, workflow_state, completed_on, 
					TIMESTAMPDIFF(SECOND, creation, completed_on) / 3600 as time_taken
	 				 from (SELECT completed_by, status, reference_name, creation, workflow_state, 
						(
							SELECT creation FROM `tabWorkflow Action` w 
							WHERE w.reference_name = wa.reference_name 
								AND w.workflow_state != wa.workflow_state 
								AND w.creation > wa.creation 
							ORDER BY w.creation ASC 
							LIMIT 1
						) AS completed_on
					FROM 
						`tabWorkflow Action` wa
					WHERE
						reference_doctype = 'CAD Order' {condition}) as workflow  order by creation desc""", as_dict=1)
	return data

def get_columns(filters):
	columns = [
		{
			"label": _("CAD Order"),
			"fieldname": "reference_name",
			"fieldtype": "Link",
			"options": "CAD Order"
		},
		{
			"label": _("Workflow State"),
			"fieldname": "workflow_state",
			"fieldtype": "Data"
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data"
		},
		{
			"label": _("Start Time"),
			"fieldname": "creation",
			"fieldtype": "Datetime"
		},
		{
			"label": _("End Time"),
			"fieldname": "completed_on",
			"fieldtype": "Datetime"
		},
		{
			"label": _("Time Taken(in Hrs)"),
			"fieldname": "time_taken",
			"fieldtype": "Float"
		}
	]
	return columns

def get_conditions(filters):
	condition = ''
	if order:=filters.get("cad_order"):
		condition += f"and reference_name = '{order}'"
	if state:=filters.get("workflow_state"):
		condition += f"and workflow_state like '%{state}%'"
	return condition