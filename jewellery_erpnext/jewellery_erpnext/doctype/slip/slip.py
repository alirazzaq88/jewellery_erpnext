# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form

class Slip(Document):
	def on_submit(self):
		# Create Operation Card
		oc_doc = frappe.new_doc('Operation Card')
		oc_doc.purity = self.purity
		oc_doc.operation = self.current_operation
		oc_doc.slip = self.name
		oc_doc.save()
		frappe.msgprint(f"Operation Card {get_link_to_form('Operation Card', oc_doc.name)} Created !!")

		# TODO: create a material request for Gold and Alloy Gold weight will be computed from Wax Weight

