import frappe

def check_duplicates(self):
	conditions = """where item_code = %(item_code)s and price_list = %(price_list)s and name != %(name)s"""

	for field in [
		"uom",
		"valid_from",
		"valid_upto",
		"packing_unit",
		"customer",
		"supplier",
		"batch_no",
		"bom_no"]:
		if self.get(field):
			conditions += " and {0} = %({0})s ".format(field)
		else:
			conditions += "and (isnull({0}) or {0} = '')".format(field)

	price_list_rate = frappe.db.sql("""
			select price_list_rate
			from `tabItem Price`
			{conditions}
		""".format(conditions=conditions),
		self.as_dict(),)

	if price_list_rate:
		frappe.throw(_("Item Price appears multiple times based on Price List, Supplier/Customer, Currency, Item, Batch, UOM, Qty, and Dates."), ItemPriceDuplicateItem,)
