import frappe
from frappe import _
from frappe.utils import get_link_to_form
from erpnext.e_commerce.variant_selector.utils import get_item_codes_by_attributes

def validate(self, method):
	pass
	#update_item_uom_conversion(self)

def update_item_uom_conversion_from_gemstone():
	data = frappe.get_all("Gemstone Weight")
	for row in data:
		gemstone_weight_doc = frappe.get_doc("Gemstone Weight", row.name)
		attribute_filters = {'Gemstone Type': gemstone_weight_doc.gemstone_type,'Stone Shape':gemstone_weight_doc.stone_shape,'Gemstone Grade':gemstone_weight_doc.gemstone_grade,'Gemstone Size':gemstone_weight_doc.gemstone_size}
		item_list = get_item_codes_by_attributes(attribute_filters)
		if item_list:
			for item in item_list:
					doc = frappe.get_doc("Item", item)
					to_remove = [d for d in doc.uoms if d.uom == "Pcs"]
					for d in to_remove:
						doc.remove(d)
					doc.append("uoms",{
						'uom': "Pcs",
						'conversion_factor' : gemstone_weight_doc.weight
					})
					doc.save(ignore_permissions=True)
					frappe.msgprint(_("Item {0} conversion factor updated.").format(get_link_to_form("Item", doc.name)))