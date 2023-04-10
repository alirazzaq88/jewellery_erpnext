import frappe
from frappe import _
from frappe.utils import get_link_to_form
from erpnext.e_commerce.variant_selector.utils import get_item_codes_by_attributes

def validate(self, method):
	pass
	#update_item_uom_conversion(self)

def update_item_uom_conversion_from_diamond():
	data = frappe.get_all("Diamond Weight")
	for row in data:
		diamond_weight_doc = frappe.get_doc("Diamond Weight", row.name)
		attribute_filters = {'Diamond Type': diamond_weight_doc.diamond_type,'Stone Shape':diamond_weight_doc.stone_shape,'Diamond Sieve Size':diamond_weight_doc.diamond_sieve_size}
		item_list = get_item_codes_by_attributes(attribute_filters)
		if item_list:
			for item in item_list:
					doc = frappe.get_doc("Item", item)
					to_remove = [d for d in doc.uoms if d.uom == "Pcs"]
					for d in to_remove:
						doc.remove(d)
					doc.append("uoms",{
						'uom': "Pcs",
						'conversion_factor' : diamond_weight_doc.weight
					})
					doc.save(ignore_permissions=True)
					frappe.msgprint(_("Item {0} conversion factor updated.").format(get_link_to_form("Item", doc.name)))