import frappe
from erpnext.controllers.item_variant import get_variant,create_variant
import json

@frappe.whitelist()
def set_items_from_attribute(item_template, item_template_attribute):
	item_template_attribute = json.loads(item_template_attribute)
	args = {}
	for row in item_template_attribute:
		if not row.get('attribute_value'):
			frappe.throw(f"Row: {row.get('idx')} Please select attribute value for {row.get('item_attribute')}.")
		args.update({
			row.get('item_attribute'): row.get('attribute_value')
		})
	variant = get_variant(item_template, args)
	if variant:
		return frappe.get_doc("Item",variant)
	else:
		variant = create_variant(item_template,args)
		variant.save()
		return variant

def get_variant_of_item(item_code):
	return frappe.db.get_value('Item', item_code, 'variant_of')