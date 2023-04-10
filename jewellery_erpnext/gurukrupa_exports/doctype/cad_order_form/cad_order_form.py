# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class CADOrderForm(Document):
	def on_submit(self):
		create_cad_orders(self)

	def on_cancel(self):
		delete_auto_created_cad_order(self)

	def validate(self):
		self.validate_category_subcaegory()

	def validate_category_subcaegory(self):
		for row in self.get("order_details"):
			if row.subcategory:
				parent = frappe.db.get_value("Attribute Value", row.subcategory, "parent_attribute_value")
				if row.category != parent:
					frappe.throw(_(f"Category & Sub Category mismatched in row #{row.idx}"))


def create_cad_orders(self):
	doclist = []
	for row in self.order_details:
		docname = make_cad_order(row.name, parent_doc = self)
		doclist.append(get_link_to_form("CAD Order", docname))
		
	if doclist:
		msg = _("The following {0} were created: {1}").format(
				frappe.bold(_("CAD Orders")), "<br>" + ", ".join(doclist)
			)
		frappe.msgprint(msg)

def delete_auto_created_cad_order(self):
	for row in frappe.get_all("CAD Order", filters={"cad_order_form": self.name}):
		frappe.delete_doc("CAD Order", row.name)

def make_cad_order(source_name, target_doc=None, parent_doc = None):
	def set_missing_values(source, target):
		target.cad_order_form_detail = source.name
		target.cad_order_form = source.parent
		target.cad_order_form_index = source.idx

	doc = get_mapped_doc(
		"CAD Order Form Detail",
		source_name,
		{
			"CAD Order Form Detail": {
				"doctype": "CAD Order" 
			}
		},target_doc, set_missing_values
	)

	doc.service_type = parent_doc.service_type
	doc.parcel_place = parent_doc.parcel_place
	doc.form_remarks = parent_doc.remarks
	doc.save()
	return doc.name
