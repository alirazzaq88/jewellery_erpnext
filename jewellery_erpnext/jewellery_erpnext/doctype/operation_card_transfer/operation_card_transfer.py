# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form
from frappe.model.mapper import get_mapped_doc

class OperationCardTransfer(Document):
	def on_submit(self):
		# Create a Stock Transfer and Submit Pervious Operation Card
		oc_doc = frappe.get_doc('Operation Card', self.operation_card)
		# Create a new Operation Card
		new_oc_doc = create_new_operation_card(self, oc_doc)

		# Create Material Transfer
		mt_doc = make_stock_return(oc_doc.name, oc_doc, new_oc_doc)
		mt_doc.save()
		frappe.msgprint(("Stock Entry {0} created").format(get_link_to_form("Stock Entry", mt_doc.name)))
		oc_doc.submit()


def create_new_operation_card(self, oc_doc):
	new_oc_doc = frappe.new_doc('Operation Card')
	new_oc_doc.production_order = oc_doc.production_order
	new_oc_doc.purity = oc_doc.purity
	new_oc_doc.item_code = oc_doc.item_code
	new_oc_doc.operation = self.next_operation
	new_oc_doc.previous_operation_card = self.operation_card
	new_oc_doc.save()
	frappe.msgprint(("Operation Card {0} created").format(get_link_to_form("Operation Card", new_oc_doc.name)))
	return new_oc_doc


def make_stock_return(source_name, oc_doc, self, target_doc=None):
	# warehouse = frappe.db.get_value('Operation Warehouse', {'parent': source_name}, 'warehouse')
	
	warehouse_details = get_warehouse_from_operation_card(source_name)
	warehouse = warehouse_details[0].get('warehouse') if warehouse_details else None

	def set_missing_values(source, target):
		target.stock_entry_type = 'Material Transfer For Manufacture'
		target.operation_card = self.name
		target.items = []
		target.inventory_dimension = 'Operation Card'
		bom = frappe.db.sql(f"""
							SELECT soi.bom
							FROM `tabSales Order Item` soi
							JOIN `tabProduction Order` po ON po.sales_order_item = soi.name
							WHERE po.name = '{target.production_order}' 
				""", as_dict=True)[0].get('bom')
		target.from_bom=1
		target.bom_no = bom
		l1 = oc_doc.get_external_in_weight()
		l2 = oc_doc.get_loss_weight()
		final_l = []
		for elem1 in l1:
			match_found = False
			for elem2 in l2:
				if elem1['item_code'] == elem2['item_code']:
					match_found = True
					new_elem = elem1.copy()
					new_elem['gross_wt'] -= elem2['gross_wt']
					final_l.append(new_elem)
					break
			if not match_found:
				final_l.append(elem1)

		for i in final_l:
			target.append('items', {
				'item_code':i.get('item_code'),
				'qty': i.get('gross_wt'),
				'operation_card': self.name,
				's_warehouse': warehouse,
				't_warehouse': get_warehouse_from_operation_card(self.name)[0].get('warehouse')
			})


	doclist = get_mapped_doc(
		"Operation Card",
		source_name,
		{
			"Operation Card": {
				"doctype": "Stock Entry"
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist

@frappe.whitelist()
def get_warehouse_from_operation_card(source_name):
 	return frappe.db.sql(f"""
				SELECT opw.warehouse
				FROM `tabOperation Warehouse` opw 
				JOIN `tabOperation Card` oc ON oc.operation = opw.parent
				WHERE oc.name = '{source_name}' 
	""", as_dict=True)
	# warehouse_details
	# warehouse = warehouse_details[0].get('warehouse') if warehouse_details else None