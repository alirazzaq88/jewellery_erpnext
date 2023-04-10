import frappe
from frappe import _
from frappe.utils import get_link_to_form

def validate(self, method):
	self.defualt_specifications = frappe.db.get_value('BOM', {'name': self.bom_no}, 'defualt_specifications')
	self.speifications = frappe.db.get_value('BOM', {'name': self.bom_no}, 'modified_specifications')
	self.remark = frappe.db.get_value('Sales Order Item', {'parent': self.sales_order}, 'remarks')
	self.metal_purity = frappe.db.get_value('BOM Metal Detail', {'parent': self.bom_no}, 'purity_percentage')

	if self.get("is_combine"):
		set_required_item_from_wo(self)
	elif self.get("job_card_details"):
		self.job_card_details = []
		self.set_required_items()
		self.set_work_order_operations()

@frappe.whitelist()
def get_work_orders(self):
	if not self.get("is_combine"):
		return
	operations = frappe.get_list("Operation",{"combine_job_card":1},pluck='name')
	ops = ', '.join(map(frappe.db.escape,operations))
	work_orders = frappe.db.sql(f"""SELECT work_order, item_code FROM `tabJob Card` WHERE docstatus != 2 AND operation IN ({ops}) 
								AND status = 'Open' AND work_order not in (select wod.work_order from `tabWork Order Details` wod where wod.docstatus!=2)
								GROUP BY work_order HAVING COUNT(DISTINCT operation) = {len(operations)}""", as_dict=True)
	
	if not work_orders:
		frappe.msgprint("No pending Work Orders")
		return
	for wo in work_orders:
		self.append("work_order_details",{
			"item_code": wo.item_code,
			"work_order": wo.work_order
		})
	if operations:
		self.operations = []
		for operation in operations:
			self.append("operations",{
				"operation": operation,
				"status":"Pending",
				"time_in_mins": 1
			})

def set_required_item_from_wo(self):
	if self.is_new():
		self.required_items = []
	wo = {row.work_order for row in self.work_order_details}
	if len(self.required_items):
		# for row in self.required_items:
		# 	if row.work_order not in wo:
		# 		frappe.db.delete("Work Order Item", row.name)
		return
	ops = frappe.get_list("Operation",{"combine_job_card":1},pluck='name')
	item_list = frappe.get_list("Work Order Item",{"parent":["in",wo],"operation":["in",ops]},"*")
	for row in item_list:
		self.append("required_items",{
			"operation": row.operation,
			"item_code": row.item_code,
			"item_name": row.item_name,
			"description": row.description,
			"source_warehouse": row.source_warehouse,
			"required_qty": row.required_qty,
			"transferred_qty": row.transferred_qty,
			"allow_alternative_item": row.allow_alternative_item,
			"rate": row.rate,
			"consumed_qty": row.consumed_qty,
			"returned_qty": row.returned_qty,
			"include_item_in_manufacturing": row.include_item_in_manufacturing,
			"work_order": row.parent
		})
	self.set_available_qty()

def before_save(self, method):
	# Set Warehouses and Operations
	self.transfer_material_against = 'Job Card'
	js_values = frappe.db.get_value('Jewellery Settings', 'Jewellery Settings', '*', as_dict=True)
	set_warehouses(self, js_values)
	set_reference_child_table_in_ri(self) # Set Reference Doctype and Reference Docname In Required Items
	set_defualt_operations(self, js_values)
	set_operation_warehouses(self, js_values)
	set_operation_in_required_item(self)
	set_operations(self)
	validate_operations(self)

def set_warehouses(self, js_values):
	self.source_warehouse = js_values.get('source_warehouse')
	self.wip_warehouse = js_values.get('work_in_progress')
	self.fg_warehouse = js_values.get('target_warehouse')
	self.scrap_warehouse = js_values.get('scrap_warehouse')
	
	
def set_defualt_operations(self, js_values):
	self.metal_operation = js_values.get('metal_operation')
	self.diamond_operation = js_values.get('diamond_operation')
	self.gemstone_operation = js_values.get('gemstone_operation')
	self.finding_operation = js_values.get('finding_operation')
	self.other_wt_operation = js_values.get('other_operation')
	

def set_operation_warehouses(self, js_values):
	self.diamond_warehouse = js_values.get('diamond_warehouse')
	self.gemstone_warehouse = js_values.get('gemstone_warehouse')
	self.finding_warehouse = js_values.get('finding_warehouse')
	self.other_wt_warehouse = js_values.get('other_warehouse')
	self.metal_warehouse = js_values.get('metal_warehouse')

def set_operation_in_required_item(self):
	for operation in self.required_items:
		if operation.item_code.startswith("M"):
			if not operation.operation:
				operation.operation=self.metal_operation
			if frappe.db.exists('BOM Metal Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}):
				operation.reference_doctype = "BOM Metal Detail"
				operation.reference_docname = frappe.db.get_value('BOM Metal Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'name')
			operation.source_warehouse=self.metal_warehouse
		elif operation.item_code.startswith("D"):
			if not operation.operation:
				operation.operation=self.diamond_operation

			# Set Reference Child Table and its Corresponding Value in Work Order Item
			if frappe.db.exists('BOM Diamond Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}):
				operation.reference_doctype = "BOM Diamond Detail"
				operation.reference_docname = frappe.db.get_value('BOM Diamond Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'name')
				operation.pcs = frappe.db.get_value('BOM Diamond Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'pcs')
			operation.source_warehouse=self.diamond_warehouse
		elif operation.item_code.startswith("G"):
			if not operation.operation:
				operation.operation=self.gemstone_operation
			# Set Reference Child Table and its Corresponding Value in Work Order Item
			if frappe.db.exists('BOM Gemstone Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}):
				operation.reference_doctype = "BOM Gemstone Detail"
				operation.reference_docname = frappe.db.get_value('BOM Gemstone Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'name')
				operation.pcs = frappe.db.get_value('BOM Gemstone Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'pcs')
			operation.source_warehouse=self.gemstone_warehouse
		elif operation.item_code.startswith("F"):
			if not operation.operation:
				operation.operation=self.finding_operation
			# Set Reference Child Table and its Corresponding Value in Work Order Item
			if frappe.db.exists('BOM Finding Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}):
				operation.reference_doctype = "BOM Finding Detail"
				operation.reference_docname = frappe.db.get_value('BOM Finding Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'name')
			operation.source_warehouse=self.finding_warehouse
		else:
			if not operation.operation:
				operation.operation=self.other_wt_operation
			if frappe.db.exists('BOM Other Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}):
				operation.reference_doctype = "BOM Other Detail"
				operation.reference_docname = frappe.db.get_value('BOM Other Detail', {'parent': self.bom_no, 'item_variant': operation.item_code}, 'name')
			operation.source_warehouse=self.other_wt_warehouse

def set_operations(self):
	if not self.mould:
		operation = frappe.db.get_list("Operation")
		opera = [
			self.metal_operation,
			self.diamond_operation,
			self.gemstone_operation,
			self.finding_operation,
			self.other_wt_operation,
		]
		opera.extend(row.name for row in operation)
		if not self.operations:
			for r in set(opera):
				operation_time = frappe.db.get_value("Operation", r, 'operation_time')
				workstation = frappe.db.get_value("Operation", r, 'workstation')
				self.append('operations', {
						'operation': r,
						'time_in_mins':operation_time,
						'workstation':workstation
					})
			# for row in list(operation):
			# 	operation_time = frappe.db.get_value("Operation", row, 'operation_time')
			# 	workstation = frappe.db.get_value("Operation", r, 'workstation')
			# 	self.append('operations', {
			# 			'operation': row.name,
			# 			'time_in_mins':operation_time,
			# 			'workstation':workstation
			# 		})

	else:
		operation = frappe.db.get_list("Operation", filters = {'without_mould':0})

		if not self.operations:
			for row in list(operation):
				operation_time = frappe.db.get_value("Operation", row, 'operation_time')
				workstation = frappe.db.get_value("Operation", row, 'workstation')
				self.append('operations', {
						'operation': row.name,
						'time_in_mins':operation_time,
						'workstation':workstation
					})

def validate_operations(self):
	if self.qty != 1: frappe.throw("Quantity To Manufacture should be 1")
	operation_list = [row.operation for row in self.operations]
	# set_operations()
	for row in self.required_items:
		if row.operation and row.operation not in operation_list:
			frappe.throw(f"Operation {row.operation} not defined in Operations.")
	
# Overriden Function For Creating Material Request in Work Order
@frappe.whitelist()
def create_material_request(docname):
	doc = frappe.get_doc("Work Order", docname)
	item_dict = {}

	for row in doc.required_items:
		if not item_dict.get(row.operation+row.source_warehouse):
			item_dict[row.operation+row.source_warehouse] = [row]
		else:
			item_dict[row.operation+row.source_warehouse].append(row)
	if item_dict:

		for k, values in item_dict.items():
			mr_doc = frappe.new_doc("Material Request")
			mr_doc.company = doc.company
			mr_doc.material_request_type = "Material Transfer"
			mr_doc.transaction_date = doc.planned_start_date
			mr_doc.schedule_date = doc.planned_start_date
			mr_doc.work_order = doc.name
			# mr_doc.to_job_card = frappe.db.get_value('Job Card', {'work_order': docname, 'operation': row.operation}, 'name')
			for row in values:
				mr_doc.to_job_card = frappe.db.get_value('Job Card', {'work_order': docname, 'operation': row.operation}, 'name')
				mr_doc.job_card = frappe.db.get_value('Job Card', {'work_order': docname, 'operation': row.operation}, 'name')
				mr_doc.append("items",{
				'item_code': row.item_code,
				'qty': row.required_qty,
				'from_warehouse': row.source_warehouse,
				'warehouse':  frappe.db.get_value("Operation Warehouse",{'parent': row.operation,'company': doc.company},'warehouse'),
				'uom': frappe.db.get_value("Item", row.item_code, 'stock_uom'),
				'conversion_factor': 1,
				'stock_uom': frappe.db.get_value("Item",row.item_code,'stock_uom'),
			})
			mr_doc.save()
			frappe.msgprint(_("Material Request {0} created").format(get_link_to_form("Material Request", mr_doc.name)))

def set_reference_child_table_in_ri(self):
	pass