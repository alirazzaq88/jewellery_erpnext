# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form
from erpnext.setup.utils import get_exchange_rate
import json

class CADOrder(Document):
	def on_submit(self):
		create_line_items(self)

    
def create_line_items(self):
	# if self.workflow_state == 'Approved' and not self.item:
	item = create_item_from_cad_order(self.name)
	frappe.db.set_value(self.doctype, self.name, "item", item)
	frappe.msgprint(_("New Item Created: {0}".format(get_link_to_form("Item",item))))

def create_item_from_cad_order(source_name, target_doc=None):
	def post_process(source, target):
		target.disabled = 1
		target.is_design_code = 1
		if source.designer_assignment:
			target.designer = source.designer_assignment[0].designer

	doc = get_mapped_doc(
		"CAD Order",
		source_name,
		{
			"CAD Order": {
				"doctype": "Item",
				"field_map": {
					"category": "item_category",
					"subcategory": "item_subcategory",
					"setting_type": "setting_type"
				} 
			}
		},target_doc, post_process
	)
	doc.save()
	return doc.name

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source_name, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		quotation.cad_order_form = source_name

	if isinstance(target_doc, str):
		target_doc = json.loads(target_doc)
	if not target_doc:
		target_doc = frappe.new_doc("Quotation")
	else:
		target_doc = frappe.get_doc(target_doc)

	item = frappe.db.get_value("CAD Order", source_name, "item")
	# frappe.msgprint(target_doc)
	target_doc.append("items", {
		"item_code": item
	})
	set_missing_values(source_name, target_doc)

	return target_doc