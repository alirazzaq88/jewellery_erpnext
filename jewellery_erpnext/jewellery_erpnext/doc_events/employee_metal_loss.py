import frappe
import json

@frappe.whitelist()
def update_metal_loss(data):
    dates = json.loads(data)
    if not dates.get('from_date') or not dates.get('to_date'): 
        return frappe.throw("Please Specify From Date and To Date")

    emp_list = frappe.db.get_list('Employee', {}, 'name')

    template = """
        SELECT name
        FROM `tabEmployee Metal Loss`
        WHERE employee = %s
        AND (
            (date_from BETWEEN %s AND %s)
            OR
            (date_to BETWEEN %s AND %s)
        )
    """

    for oper in emp_list:
        data = frappe.db.sql(template, (oper.name, dates.get('from_date'), dates.get('to_date'), dates.get('from_date'), dates.get('to_date')))
        if data:
            frappe.msgprint("Record Already Exists Within Date Range")
        else:
            ml_doc = frappe.new_doc('Employee Metal Loss')
            ml_doc.employee = oper.get('name')
            ml_doc.date_from = dates.get('from_date')
            ml_doc.date_to = dates.get('to_date')
            ml_doc.save()
            if ml_doc.total_metal_loss == 0:
                frappe.delete_doc('Employee Metal Loss', ml_doc.name)
