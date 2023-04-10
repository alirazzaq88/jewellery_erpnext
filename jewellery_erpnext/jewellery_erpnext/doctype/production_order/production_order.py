# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta



class ProductionOrder(Document):
	def on_submit(self):
		# Create Material Request
		if not self.first_operation: return frappe.throw("Please Enter First Operation")
		self.create_material_requests()
		self.create_operation_card()
	
	def create_material_requests(self):
		bom_doc = frappe.db.sql(f"""
					SELECT bi.item_code, bi.qty
					FROM 
					`tabSales Order Item` soi
					LEFT JOIN `tabBOM Item` bi ON bi.parent = soi.bom 
					WHERE soi.name = '{self.sales_order_item}'
		""", as_dict=True)
		items = {}
		for row in bom_doc:
			item_type = get_item_type(row.item_code)
			if item_type not in items:
				items[item_type] = []
			items[item_type].append({'item_code': row.item_code, 'qty': row.qty})

		for item_type, val in items.items():
			mr_doc = frappe.new_doc('Material Request')
			mr_doc.material_request_type = 'Material Transfer'
			mr_doc.schedule_date = frappe.utils.nowdate()
			mr_doc.production_order = self.name
			for i in val:
				mr_doc.append('items', i)
			mr_doc.save()
		frappe.msgprint("Material Request Created !!")

	def create_operation_card(self):
		oc_doc = frappe.new_doc('Operation Card')
		oc_doc.production_order = self.name
		oc_doc.purity = self.purity
		oc_doc.item_code = self.item_code
		oc_doc.operation = self.first_operation
		oc_doc.save()
		frappe.msgprint('First Operation Card Created !!')


def get_item_type(item_code):
	if item_code.startswith('M'):
		return 'metal_item'
	elif item_code.startswith('D'):
		return 'diamond_item'
	elif item_code.startswith('G'):
		return 'gemstone_item'
	elif item_code.startswith('F'):
		return 'finding_item'
	else:
		return 'other_item'

@frappe.whitelist()
def make_production_order(sales_order):
	so_doc=frappe.get_doc('Sales Order', sales_order)
	for item in so_doc.items:
		for _ in range(int(item.qty)):
			bom_metal_detail = frappe.db.sql(f"""
								SELECT
								av.purity_percentage
								FROM `tabBOM Metal Detail` tmd
								LEFT JOIN `tabAttribute Value` av ON av.name = tmd.metal_purity
								WHERE tmd.parent = '{item.bom}'
								""", as_dict=True)
			purity_sequence = 0
			for purity in bom_metal_detail:
				purity_sequence += 1
				po_doc = frappe.new_doc('Production Order')
				po_doc.purity_sequence = purity_sequence
				po_doc.purity = purity.purity_percentage
				po_doc.item_code = item.item_code
				po_doc.sales_order_item = item.name
				po_doc.save()

	frappe.msgprint('Production Orders Created !!')


@frappe.whitelist()
def get_item_code(sales_order_item):
	return frappe.db.get_value('Sales Order Item', sales_order_item, 'item_code')