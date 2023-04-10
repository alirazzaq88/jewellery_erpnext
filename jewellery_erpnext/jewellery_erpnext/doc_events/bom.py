import frappe
from frappe.utils import flt
from erpnext.controllers.item_variant import get_variant,create_variant
from jewellery_erpnext.jewellery_erpnext.doc_events.bom_utils import set_bom_rate, calculate_gst_rate, set_bom_item_details


def before_validate(self,method):
	system_item_validation(self)
	set_item_variant(self)
	set_bom_items(self)

def validate(self,method):
	calculate_metal_qty(self)
	calculate_diamond_qty(self)
	calculate_total(self)
	set_bom_rate(self)
	set_sepecifications(self)

def on_update(self,method):
	pass

def on_cancel(self, method):
	pass
	

def on_submit(self, method):
	if self.bom_type == 'Template':
		return frappe.throw("Template BOM Can't Be Submitted")

def system_item_validation(self):
	is_system_item = frappe.db.get_value("Item",self.item,'is_system_item')
	if is_system_item:
		frappe.throw(f'Cannot create BOM for system item {self.item}.')

def set_item_variant(self):
	# Check if the bom_type is 'Template' or 'Quotation', if so, return
	if self.bom_type in ['Template', 'Quotation']: return
	bom_tables = ['metal_detail','diamond_detail','gemstone_detail','finding_detail']
	attributes = {}

	for bom_table in bom_tables:
		# Check if the current bom table exists
		if self.get(bom_table):
			# Loop through the rows of the bom table
			for row in self.get(bom_table):
				# Get the template document for the current item
				template = frappe.get_doc("Item",row.item)
				if template.name not in attributes: # If the attributes for the current item have not been fetched yet
					attributes[template.name] = [attr.attribute for attr in template.attributes] # Store the attributes in the dictionary
				# Create a dictionary of the attribute values from the row
				args = {attr: row.get(attr.replace(" ", "_").lower()) for attr in attributes[template.name] if row.get(attr.replace(" ", "_").lower())}
				variant = get_variant(row.item, args) # Get the variant for the current item and attribute values
				if variant:
					row.item_variant = variant
				else:
					# Create a new variant
					variant = create_variant(row.item,args)
					variant.save()
					row.item_variant = variant.name


def set_bom_items(self):
	"""
		Sets BOM Items Based On METAL, DIAMOND, GEMSTONE, FINDING Child Tables.
		If BOM Type is TEMPLATE or QUOTATION set defualt Item from Jewellery Settings to avoid garbage items creation.
	"""
	# Place a dummy Item if Bom type is Template or Quotation
	if self.bom_type in ['Template', 'Quotation']:
		defualt_item = frappe.db.get_value('Jewellery Settings', 'Jewellery Settings', 'defualt_item')
		self.items = [] 
		self.append('items',{
			'item_code': defualt_item,
			'is_variant': 1,
			'qty': 1,
			'uom': frappe.db.get_value("Item",defualt_item,'stock_uom'),
			'rate': 0
		})
	else:
		# Set Item Based On Child Tables 
		_set_bom_items_by_child_tables(self)


def _set_bom_items_by_child_tables(self):
	bom_items = {}
	bom_items.update({row.item_variant:row.quantity for row in self.metal_detail if row.quantity})
	bom_items.update({row.item_variant:row.quantity for row in self.diamond_detail if row.quantity})
	bom_items.update({row.item_variant:row.quantity for row in self.gemstone_detail if row.quantity})
	bom_items.update({row.item_variant:row.quantity for row in self.finding_detail if row.quantity})

	if bom_items:
		items = frappe.get_all("Jewellery System Item",{'parent':'Jewellery Settings'},'item_code')
		item_list = [row.get('item_code') for row in items]
		to_remove = [d for d in self.items if d.is_variant or frappe.db.get_value("Item",d.item_code,'variant_of') in item_list]
		for d in to_remove:
			self.remove(d)
		for item_code, qty in bom_items.items():
			self.append('items',{
				'item_code': item_code,
				'is_variant': 1,
				'qty': qty,
				'uom': frappe.db.get_value("Item",item_code,'stock_uom'),
				'rate': 0
			})


def update_item_price(self):
	if frappe.db.exists("Item Price",{"item_code":self.item,"price_list":self.buying_price_list,"bom_no":self.name}):
		name = frappe.db.get_value("Item Price",{"item_code":self.item,"price_list":self.buying_price_list,"bom_no":self.name},'name')
		item_doc = frappe.get_doc("Item Price",name)
		item_doc.db_set("price_list_rate",self.total_cost)
		item_doc.db_update()
	else:
		_create_new_price_list(self)


def _create_new_price_list(self):
	item_price = frappe.new_doc("Item Price")
	item_price.price_list = self.buying_price_list
	item_price.item_code = self.item
	item_price.bom_no = self.name
	item_price.price_list_rate = self.total_cost
	item_price.save()

def calculate_metal_qty(self):
	if self.metal_detail:
		for row in self.metal_detail:
			if row.cad_weight and row.cad_to_finish_ratio:
				row.quantity = flt(row.cad_weight * row.cad_to_finish_ratio / 100)

def calculate_diamond_qty(self):
	if self.diamond_detail:
		for row in self.diamond_detail:
			if row.stone_shape == "Round" and row.pcs and row.weight_per_pcs:
				row.quantity = flt(row.pcs * row.weight_per_pcs)

def calculate_total(self):
	"""Calculate the total weight of metal, diamond, gemstone, and finding.
		Also calculate the gold to diamond ratio, and the diamond ratio.
	"""
	self.total_metal_weight = sum(row.quantity for row in self.metal_detail)
	self.diamond_weight = sum(row.quantity for row in self.diamond_detail)
	self.total_gemstone_weight = sum(row.quantity for row in self.gemstone_detail)
	self.gemstone_weight = self.total_gemstone_weight
	self.finding_weight = sum(row.quantity for row in self.finding_detail)
	self.total_diamond_pcs = sum(flt(row.pcs) for row in self.diamond_detail)
	self.total_gemstone_pcs = sum(flt(row.pcs) for row in self.gemstone_detail)

	self.metal_and_finding_weight = flt(self.total_metal_weight) + flt(self.finding_weight)
	self.gold_to_diamond_ratio = flt(self.metal_and_finding_weight) / flt(self.diamond_weight) if self.diamond_weight else 0
	self.diamond_ratio = flt(self.diamond_weight) / flt(self.total_diamond_pcs) if self.total_diamond_pcs else 0
	self.gross_weight = flt(self.metal_and_finding_weight) + flt(self.diamond_weight) + flt(self.gemstone_weight) + flt(self.total_other_weight)

def set_sepecifications(self):
	"""
		Sets Defualt Specifications(For Template BOM) and Modified Specifications FOR BOM
	"""
	fields_list = ['item_category', 'item_subcategory', 'product_size', 'gold_target', 'diamond_target', 'metal_colour', 'enamal', 'rhodium', 'gemstone_type', 'gemstone_quality', 'changeable', 'hinges', 'back_belt_patti', 'black_beed', 'black_beed_line', 'screw_type', 'hook_type', 'lock_type', '2_in_1', 'kadi_type', 'chain', 'chain_type', 'chain_length', 'customer_chain', 'chain_weight', 'detachable', 'total_length', 'back_chain', 'back_chain_size', 'back_side_size', 'chain_size', 'kadi_to_mugappu', 'space_between_mugappu', 'breadth', 'width', 'back_belt_length']
	
	# Set Defualt Specification For Template BOM
	if self.bom_type == 'Template':
		bom = frappe.db.get_list('BOM', {'name': self.name}, '*')
		if bom:
			specifications = ''.join(f"{key} - {val} \n" for key, val in bom[0].items() if key in fields_list and val != None)
			self.defualt_specifications = specifications
	else:
		set_specifications_for_modified_bom(self, fields_list)

def set_specifications_for_modified_bom(self, fields_list):
	"""
		Set Modified Specifications Based On Values Changed From Defualt BOM.
		Defualt Specifications and Modified Specifications are `TEXT` fields.
	"""
	temp_bom = frappe.db.get_list('BOM', {'item': self.item, 'bom_type': 'Template'}, '*')
	temp_bom_dict = {}
	if temp_bom:
		for key, val in temp_bom[0].items():
			if key in fields_list:
				temp_bom_dict[key] = val
	modified_specifications = ''
	if self.is_new():
		self.defualt_specifications = ''.join(f"{key} - {val} \n" for key, val in temp_bom_dict.items())
		return 

	new_fields = [{"item_category": self.item_category}, {"item_subcategory": self.item_subcategory}, {"product_size": self.product_size}, {"gold_target": self.gold_target}, {"diamond_target": self.diamond_target}, {"metal_colour": self.metal_colour}, {"enamal": self.enamal}, {"rhodium": self.rhodium}, {"gemstone_type": self.gemstone_type}, {"gemstone_quality": self.gemstone_quality}, {"changeable": self.changeable}, {"hinges": self.hinges}, {"back_belt_patti": self.back_belt_patti}, {"black_beed": self.black_beed}, {"black_beed_line": self.black_beed_line}, {"screw_type": self.screw_type}, {"hook_type": self.hook_type}, {"lock_type": self.lock_type}, {"kadi_type": self.kadi_type}, {"chain": self.chain}, {"chain_type": self.chain_type}, {"chain_length": self.chain_length}, {"customer_chain": self.customer_chain}, {"chain_weight": self.chain_weight}, {"detachable": self.detachable}, {"total_length": self.total_length}, {"back_chain": self.back_chain}, {"back_chain_size": self.back_chain_size}, {"back_side_size": self.back_side_size}, {"chain_size": self.chain_size}, {"kadi_to_mugappu": self.kadi_to_mugappu}, {"space_between_mugappu": self.space_between_mugappu}, {"breadth": self.breadth}, {"width": self.width}, {"back_belt_length": self.back_belt_length}]
	new_dict = {}
	for i in new_fields:
		for key, val in i.items():
			new_dict[key] = val

	for key, val in new_dict.items():
		if temp_bom_dict.get(key):
			temp_bom_val = temp_bom_dict[key]
			if val != temp_bom_val and val:
				modified_specifications += f"{key} - {val} \n"
	self.defualt_specifications = ''.join(f"{key} - {val} \n" for key, val in temp_bom_dict.items() if val != None)
	self.modified_specifications = modified_specifications