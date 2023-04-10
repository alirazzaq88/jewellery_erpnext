import frappe
from frappe.model.mapper import get_mapped_doc
from jewellery_erpnext.jewellery_erpnext.doc_events.bom_utils import set_bom_rate, calculate_gst_rate, set_bom_item_details


def validate(self, method):
	create_new_bom(self)
	calculate_gst_rate(self)
	set_bom_item_details(self)
	
def on_submit(self, method):
	submit_bom(self)

def on_cancel(self, method):
	cancel_bom(self)

def create_new_bom(self):
	"""
		This Function Creates Sales Order Type BOM from Quotation Bom 
	"""
	for row in self.items:
		if not row.bom and frappe.db.exists("BOM",row.quotation_bom):
			create_sales_order_bom(self, row)

def create_sales_order_bom(self, row):
	doc = get_mapped_doc("BOM", row.quotation_bom, {
					"BOM": {
						"doctype": "BOM",
					}
				}, ignore_permissions = True)
	try:
		doc.is_default = 1
		doc.bom_type = 'Sales Order'
		doc.gold_rate_with_gst = self.gold_rate_with_gst
		doc.customer = self.customer
		doc.selling_price_list = self.selling_price_list
		doc.reference_doctype = 'Sales Order'
		doc.reference_docname = self.name
		doc.save(ignore_permissions = True)
		for diamond in doc.diamond_detail:
			if row.diamond_grade: diamond.diamond_grade = row.diamond_grade
			else:
				diamond_grade_1 = frappe.db.get_value('Customer Diamond Grade', 
										{'parent': doc.customer, 'diamond_quality': row.diamond_quality}, 
										'diamond_grade_1')

				if diamond_grade_1: diamond.diamond_grade = diamond_grade_1
			if row.diamond_quality: diamond.quality = row.diamond_quality
			
		# This Save will Call before_save and validate method in BOM and Rates Will be Calculated as diamond_quality is calculated too
		doc.save(ignore_permissions = True)
		row.bom = doc.name
		row.gold_bom_rate = doc.gold_bom_amount
		row.diamond_bom_rate = doc.diamond_bom_amount
		row.gemstone_bom_rate = doc.gemstone_bom_amount
		row.other_bom_rate = doc.other_bom_amount
		row.making_charge = doc.making_charge
		row.bom_rate = doc.total_bom_amount
		row.rate = doc.total_bom_amount
		self.total = doc.total_bom_amount
	except Exception as e:
		frappe.logger("utils").exception(e)

def submit_bom(self):
	for row in self.items:
		if row.bom:
			bom = frappe.get_doc("BOM",row.bom)
			bom.submit()

def cancel_bom(self):
	for row in self.items:
		if row.bom:
			bom = frappe.get_doc("BOM",row.bom)
			bom.is_active = 0
			row.bom = ''