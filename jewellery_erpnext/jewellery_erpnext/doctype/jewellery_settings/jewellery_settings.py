# Copyright (c) 2022, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from jewellery_erpnext.jewellery_erpnext.doc_events.diamond_weight import update_item_uom_conversion_from_diamond
from jewellery_erpnext.jewellery_erpnext.doc_events.gemstone_weight import update_item_uom_conversion_from_gemstone

class JewellerySettings(Document):
	@frappe.whitelist()
	def update_uom_conversion_in_variant(self):
		update_item_uom_conversion_from_diamond()
		update_item_uom_conversion_from_gemstone()
		return "Queued for updating Item variants.It may take a few minutes."

