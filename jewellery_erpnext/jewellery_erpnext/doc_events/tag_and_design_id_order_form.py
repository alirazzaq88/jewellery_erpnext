import frappe
from frappe import _
from frappe.utils import get_link_to_form

def on_submit(self, method):
	create_tag_and_design_order(self)

def on_cancel(self, method):
	delete_auto_created_tag_and_design_order(self)

def create_tag_and_design_order(self):
	for row in self.order_details:
		doc = frappe.new_doc("Tag and Design ID Order")
		doc.tag_and_design_id_order_form = self.name
		doc.tag_and_design_id_order_form_detail = row.name
		doc.tag_and_design_id_order_form_index =  str(int(row.idx))
		doc.save()
		frappe.msgprint(_("Tag and Design ID Order {0} created").format(get_link_to_form("Tag and Design ID Order", doc.name)))

def delete_auto_created_tag_and_design_order(self):
	for row in frappe.get_all("Tag and Design ID Order", filters={"tag_and_design_id_order_form": self.name}):
		frappe.delete_doc("Tag and Design ID Order", row.name)