import frappe
from erpnext.controllers.item_variant import get_variant,create_variant
from frappe import _

@frappe.whitelist()
def item_attribute_query(doctype, txt, searchfield, start, page_len, filters):
	args = {
		'item_attribute': filters.get("item_attribute"),
		"txt": "%{0}%".format(txt),
	}
	condition = ''
	if filters.get("customer_code"):
		args["customer_code"] = filters.get("customer_code")
		condition = """and attribute_value in (select diamond_quality from `tabCustomer Diamond Grade` where parent = %(customer_code)s)""" 

	if filters.get("metal_touch"):
		args["metal_touch"] = filters.get("metal_touch")
		condition += "and attribute_value in (select av.name from `tabAttribute Value` av where metal_touch = %(metal_touch)s)"

	if (filters.get("parent_attribute_value")):
		args['parent_attribute_value'] = filters.get("parent_attribute_value")
		item_attribute = frappe.db.sql("""select attribute_value
				from `tabItem Attribute Value`
					where parent = %(item_attribute)s 
					and attribute_value like %(txt)s
					and parent_attribute_value = %(parent_attribute_value)s
				""",args)
	else:
		item_attribute = frappe.db.sql(f"""select attribute_value
				from `tabItem Attribute Value`
					where parent = %(item_attribute)s 
					and attribute_value like %(txt)s {condition}
				""",args)
	return item_attribute if item_attribute else []

@frappe.whitelist()
def set_wo_items_grade(doctype, txt, searchfield, start, page_len, filters):
	bom_no = frappe.db.get_value('Sales Order Item', {'parent': filters.get('sales_order')}, 'bom')
	frappe.logger('utils').debug(filters.get('sales_order'))
	diamond_quality = frappe.db.get_value("BOM Diamond Detail", {'parent': bom_no}, 'quality')
	frappe.logger('utils').debug(diamond_quality)
	data = frappe.db.sql(
		"""
		SELECT 
		dg.diamond_grade_1,
		dg.diamond_grade_2,
		dg.diamond_grade_3,
		dg.diamond_grade_4
		FROM
		`tabSales Order` so
		LEFT JOIN
		`tabCustomer` cust ON cust.name = so.customer
		LEFT JOIN
		`tabCustomer Diamond Grade` dg
		ON dg.parent = cust.name
		WHERE
		so.name = '%s'
		AND dg.diamond_quality = '%s'
		
		"""%(filters.get('sales_order'), diamond_quality)
	)
	return tuple(zip(*data))

@frappe.whitelist()
def get_item_code(item_code, grade):
	variant_of = frappe.db.get_value('Item', item_code, 'variant_of')
	if variant_of != 'D':
		return item_code
	attr_val = frappe.db.get_list("Item Variant Attribute", {'parent': item_code}, ['attribute','attribute_value'])
	args = {}
	for attr in attr_val:
		if attr.get("attribute") == 'Diamond Grade':
			attr['attribute_value'] = grade
		args[attr.get("attribute")] = attr.get("attribute_value")

	variant = get_variant(variant_of, args)
	if not variant:
		variant = create_variant(variant_of,args)
		variant.save()
		return variant.name
	return variant

@frappe.whitelist()	
def set_metal_purity(sales_order):
	bom = frappe.db.get_value('Sales Order Item', {'parent': sales_order}, 'bom')
	remark = frappe.db.get_value('Sales Order Item', {'parent': sales_order}, 'remarks')
	metal_purity = frappe.db.get_value('BOM Metal Detail', {'parent': bom}, 'purity_percentage')
	return {"metal_purity": metal_purity, "remark": remark}

@frappe.whitelist()
def get_scrap_items(doctype, txt, searchfield, start, page_len, filters):
	work_order = filters.get('work_order')
	data = frappe.db.sql(
		"""
		SELECT
		woi.item_code
		FROM 
		`tabWork Order Item` woi 
		WHERE woi.parent = '%s'
		GROUP BY
		woi.item_code 
		"""%(work_order)
	)
	data = list(data)
	data.append(('METAL LOSS',))
	data = tuple(data)
	return data

@frappe.whitelist()
def diamond_grades_query(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	args = {
		'customer': filters.get("customer"),
	}
	diamond_quality = None
	
	diamond_quality = frappe.db.sql("""select diamond_quality
			from `tabCustomer Diamond Grade`
				where parent = %(customer)s
			""",args)
			
	if diamond_quality:
		return diamond_quality
	else:
		frappe.throw(_('Diamond Qulity not Found. Please define the Diamond quality in <strong>Customer</strong>'))


@frappe.whitelist()
def get_production_item(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""
		SELECT it.name from 
		`tabItem` it
		WHERE it.item_group = 'Designs'
		"""
	)

@frappe.whitelist()
def set_warehouses(filters=None):
	js_values = frappe.db.get_value('Jewellery Settings', 'Jewellery Settings', '*', as_dict=True)
	return js_values

@frappe.whitelist()
def get_wo_operations(doctype, txt, searchfield, start, page_len, filters):
	template = f"""
		SELECT 
		woo.operation 
		FROM `tabWork Order Operation` woo
		WHERE woo.parent = '{filters.get('work_order')}'
		"""
	return frappe.db.sql(
		template
	)

@frappe.whitelist()
def get_parcel_place(doctype, txt, searchfield, start, page_len, filters):
	condition = ''
	if customer:=filters.get("customer_code"):
		condition = """where name in (select parcel_place from `tabParcel Place MultiSelect` where parent = %s)"""%frappe.db.escape(customer)

	return frappe.db.sql(
		"""
		SELECT parcel_place from 
		`tabParcel Place List`
		{0}
		""".format(condition)
	)