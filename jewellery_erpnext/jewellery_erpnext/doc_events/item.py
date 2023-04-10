import frappe
import json
from frappe.utils import flt


def before_validate(self,method):
	add_item_attributes(self)

def validate(self, method):
	system_item_restriction(self)
	update_item_uom_conversion(self)
	set_attribute_and_value_in_description(self)

def before_save(self, method):
	pass
	#update_item_uom_conversion(self)

def on_trash(self, method):
	if frappe.session.user != "Administrator" and self.is_system_item:
		frappe.throw("Can not delete the system item.")

def system_item_restriction(self):
	items = frappe.get_all("Jewellery System Item",{'parent':'Jewellery Settings'},'item_code')
	item_list = [row.get('item_code') for row in items]
	if (
		not self.is_new()
		and frappe.session.user != "Administrator"
		and self.is_system_item
		and (self.item_code in item_list or self.variant_of in item_list)
	):
		frappe.throw("You can not edit system item. Please contact administrator to edit the item.")
	if self.item_code in item_list and not self.is_system_item: 
		self.is_system_item = 1

def add_item_attributes(self):
	if self.has_variants and self.subcategory and not self.attributes:
		item_attributes = frappe.get_all("Attribute Value Item Attribute Detail",{'parent': self.subcategory},'item_attribute',order_by='idx asc')
		if item_attributes:
			self.attributes = []
			for row in item_attributes:
				self.append('attributes',{
					'attribute': row.item_attribute,
					'numeric_values': frappe.db.get_value("Item Attribute",row.item_attribute,'numeric_values'),
					'from_range': frappe.db.get_value("Item Attribute",row.item_attribute,'from_range'),
					'to_range': frappe.db.get_value("Item Attribute",row.item_attribute,'to_range'),
					'increment': frappe.db.get_value("Item Attribute",row.item_attribute,'increment')
				})

def update_item_uom_conversion(self):
	if self.attributes:
		attribute_list = [row.attribute for row in self.attributes]
		weight = set_diamond_attribute_weight(self,attribute_list)
		if not weight:
			weight = set_gemstone_attribute_weight(self,attribute_list)
		if weight:
			to_remove = [d for d in self.uoms if d.uom == "Pcs"]
			for d in to_remove:
				self.remove(d)
			self.append("uoms",{
				'uom': "Pcs",
				'conversion_factor' : weight
			})

def set_diamond_attribute_weight(self,attribute_list):
	diamond_attribute_list = ['Diamond Type', 'Stone Shape', 'Diamond Sieve Size']
	weight = 0
	if set(diamond_attribute_list).issubset(set(attribute_list)):
		attribute_filters = {}
		for row in self.attributes:
			if row.attribute == "Diamond Type":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value}) 
			if row.attribute == "Stone Shape":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value})
			if row.attribute == "Diamond Sieve Size":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value})
		if frappe.db.exists("Diamond Weight",attribute_filters):
			weight = frappe.db.get_value("Diamond Weight",attribute_filters,'weight')
	return weight or 0

def set_gemstone_attribute_weight(self,attribute_list):
	gemstone_attribute_list = ['Gemstone Type','Stone Shape','Gemstone Grade','Gemstone Size']
	weight = 0
	if set(gemstone_attribute_list).issubset(set(attribute_list)):
		attribute_filters = {}
		for row in self.attributes:
			if row.attribute == "Gemstone Type":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value}) 
			if row.attribute == "Stone Shape":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value})
			if row.attribute == "Gemstone Grade":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value})
			if row.attribute == "Gemstone Size":
				attribute_filters.update({row.attribute.replace(' ','_').lower(): row.attribute_value})
		if frappe.db.exists("Gemstone Weight",attribute_filters):
			weight = frappe.db.get_value("Gemstone Weight",attribute_filters,'weight')
	return weight
				
def set_attribute_and_value_in_description(self):
	if self.variant_of:
		description_value = "<b><u>" + self.variant_of + "</u></b><br/>"
		for d in self.get('attributes'):
			description_value += d.attribute +" : "+ d.attribute_value + "<br/>"
		self.description = description_value

@frappe.whitelist()
def calculate_item_wt_details(doc,bom=None, item=None):
	if isinstance(doc, str):
		doc = json.loads(doc)
	settings = frappe.get_doc("Jewellery Settings")
	doc["cad_to_rpt_ratio"] = settings.cad_to_rpt
	doc["estimated_rpt_wt"] = flt(doc["cad_weight"]) / flt(settings.cad_to_rpt)
	doc["rpt_to_wax_ratio"] = settings.rpt_to_wax
	doc["estimated_wax_wt"] = flt(doc["estimated_rpt_wt"]) / flt(settings.rpt_to_wax)
	doc["wax_to_10kt_gold_ratio"] = settings.wax_to_gold_10
	doc["wax_to_14kt_gold_ratio"] = settings.wax_to_gold_14
	doc["wax_to_18kt_gold_ratio"] = settings.wax_to_gold_18
	doc["wax_to_22kt_gold_ratio"] = settings.wax_to_gold_22
	doc["wax_to_silver_ratio"] = settings.wax_to_silver
	doc['estimated_10kt_gold_wt'] = flt(doc["estimated_wax_wt"]) * flt(doc["wax_to_10kt_gold_ratio"])
	doc['estimated_14kt_gold_wt'] = flt(doc["estimated_wax_wt"]) * flt(doc["wax_to_14kt_gold_ratio"])
	doc['estimated_18kt_gold_wt'] = flt(doc["estimated_wax_wt"]) * flt(doc["wax_to_18kt_gold_ratio"])
	doc['estimated_22kt_gold_wt'] = flt(doc["estimated_wax_wt"]) * flt(doc["wax_to_22kt_gold_ratio"])
	doc['estimated_silver_wt'] = flt(doc["estimated_wax_wt"]) * flt(doc["wax_to_silver_ratio"])
	if bom:
		doc["estimated_finding_gold_wt_bom"] = frappe.db.get_value("BOM",bom,'finding_weight')
	else: 
		finding_weight = frappe.db.sql(f"""SELECT 
		finding_weight 
		FROM `tabBOM` 
		WHERE item = '{item}' LIMIT 1""", as_dict=True)
		if finding_weight:
			doc["estimated_finding_gold_wt_bom"] = finding_weight[0].get('finding_weight')
	return doc