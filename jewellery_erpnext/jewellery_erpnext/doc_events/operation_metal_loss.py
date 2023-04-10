import frappe
import json


@frappe.whitelist()
def update_metal_loss(data):
    dates = json.loads(data)
    if not dates.get('from_date') or not dates.get('to_date'): 
        return frappe.throw("Please Specify From Date and To Date")

    oper_list = frappe.db.get_list('Operation', {}, 'name')

    template = """
        SELECT name
        FROM `tabOperation Metal Loss`
        WHERE operation = %s
        AND (
            (date_from BETWEEN %s AND %s)
            OR
            (date_to BETWEEN %s AND %s)
        )
    """

    for oper in oper_list:
        data = frappe.db.sql(template, (oper.name, dates.get('from_date'), dates.get('to_date'), dates.get('from_date'), dates.get('to_date')))
        if data:
            frappe.msgprint("Record Already Exists Within Date Range")
        else:
            ml_doc = frappe.new_doc('Operation Metal Loss')
            ml_doc.operation = oper.get('name')
            ml_doc.date_from = dates.get('from_date')
            ml_doc.date_to = dates.get('to_date')
            ml_doc.save()
            if ml_doc.total_metal_loss == 0:
                frappe.delete_doc('Operation Metal Loss', ml_doc.name)


