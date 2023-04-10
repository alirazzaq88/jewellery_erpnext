import frappe
from frappe.utils import flt


def calculate_gst_rate(self):
	gold_gst_rate = frappe.db.get_value(
		"Jewellery Settings", "Jewellery Settings", "gold_gst_rate"
	)
	divide_by = 100 + int(gold_gst_rate)
	self.gold_rate = self.gold_rate_with_gst * 100 / divide_by


def set_bom_rate(self):
	"""
	Calculates BOM Rate for an Item
	Takes in BOM Document as a parameter
	"""
	fields = {
		"gold_bom_rate": get_gold_rate(self),
		"diamond_bom_rate": get_diamond_rate(self),
		"gemstone_bom_rate": get_gemstone_rate(self),
		"other_bom_rate": get_other_rate(self),
		"making_charge": get_making_charges(self) or 0,
	}
	# remove None values
	fields = {k: v for k, v in fields.items() if v is not None}
	bom_fields = {
		k.replace("rate", "amount"): v for k, v in fields.items() if v is not None
	}

	# update the self object
	self.update(bom_fields)

	# Update Quotation in which current BOM is present
	frappe.db.set_value("Quotation Item", {"quotation_bom": self.name}, fields)

	# calculate and update the total bom amount
	self.total_bom_amount = sum(bom_fields.values())
	frappe.db.set_value(
		"Quotation Item",
		{"quotation_bom": self.name},
		{"bom_rate": self.total_bom_amount},
	)

	# commit the changes
	frappe.db.commit()


def get_gold_rate(self):
	# Get the metal purity from the self object or default to 0

	# Get the gold GST rate from the Jewellery Settings doctype
	gold_gst_rate = frappe.db.get_value(
		"Jewellery Settings", "Jewellery Settings", "gold_gst_rate"
	)

	# Initialize the amount variable
	amount = 0

	# Set rates in metal_detail and finding_detail child tables
	for item in self.metal_detail + self.finding_detail:
		metal_purity = item.purity_percentage or 0
		# Check if item is a customer item
		if item.is_customer_item:
			# Set rate and amount to 0 if it's a customer item
			item.rate = 0
			item.amount = 0
		else:
			# Calculate the amount using the gold rate, metal purity and GST rate
			item.rate = (
				flt(self.gold_rate_with_gst)
				* flt(metal_purity)
				/ (100 + int(gold_gst_rate))
			)
			item.amount = flt(item.quantity) * item.rate
		# Add the current item's amount to the total amount
		amount += item.amount

	# Return the total amount
	return amount


def get_diamond_rate(self):
	# Get the customer from the self object
	customer = self.customer

	# Get the diamond price list type for the customer
	cust_diamond_price_list_type = frappe.db.get_value(
		"Customer", customer, "diamond_price_list"
	)

	# Initialize the diamond amount variable
	diamond_amount = 0
	# create a dict having sieve size range with avg wt for rate acc to range
	ss_range = {}
	for diamond in self.diamond_detail:
		if not diamond.sieve_size_range:
			continue
		det = ss_range.get(diamond.sieve_size_range) or {}
		det['pcs'] = flt(det.get("pcs")) + diamond.pcs
		det['quantity'] = flt(flt(det.get("quantity")) + diamond.quantity, 3)
		det["std_wt"] = flt(flt(det['quantity'],2) / det['pcs'],3)
		ss_range[diamond.sieve_size_range] = det

	# Iterate through the diamond_detail
	for diamond in self.diamond_detail:
		det = ss_range.get(diamond.sieve_size_range) or {}
		amount = _calculate_diamond_amount(self, diamond, cust_diamond_price_list_type, det)
		diamond_amount += amount
	return diamond_amount


def _calculate_diamond_amount(self, diamond, cust_diamond_price_list_type, range_det):
	"""
	Calculates Diamond Rate for a single diamond in BOM Diamond Detail.
	Takes a single row of BOM Diamond Detail as a parameter.
	"""
	# Get the sieve size range and diameter for the current diamond
	attribute_value = frappe.db.get_value(
		"Attribute Value",
		diamond.diamond_sieve_size,
		["sieve_size_range", "diameter"],
		as_dict=1,
	)
	sieve_size_range = attribute_value.get("sieve_size_range")
	size_in_mm = attribute_value.get("diameter")

	# Create filters for retrieving the Diamond Price List
	price_list_type = cust_diamond_price_list_type
	filters = {
		"price_list": self.selling_price_list,
		"diamond_type": diamond.diamond_type,
		"stone_shape": diamond.stone_shape,
		"diamond_quality": diamond.quality,
		"price_list_type": price_list_type,
		"customer": self.customer,
	}
	if price_list_type == "Weight (in cts)":
		filters.update(
			{
				"from_weight": ["<=", range_det.get('std_wt')],
				"to_weight": [">=", range_det.get('std_wt')],
			}
		)
	elif price_list_type == "Sieve Size Range":
		filters["sieve_size_range"] = sieve_size_range
	elif price_list_type == "Size (in mm)":
		filters["size_in_mm"] = size_in_mm
	else:
		frappe.msgprint("Price List Type Not Specified")
		return 0

	# Retrieve the Diamond Price List and calculate the rate
	diamond_price_list = frappe.get_list(
		"Diamond Price List",
		filters=filters,
		fields=["rate", "handling_rate"],
		order_by="effective_from desc",
		limit=1,
	)
	if not diamond_price_list:
		frappe.msgprint(
			f"Diamond Amount for Sieve Size - {diamond.diamond_sieve_size} is 0\n Please Check if Diamond Price Exists For {filters}"
		)
		return 0

	# Get Handling Rate of the Diamond if it is a cutomer provided Diamond
	rate = (
		diamond_price_list[0].get("handling_rate")
		if diamond.is_customer_item
		else diamond_price_list[0].get("rate")
	)

	# Set the rate and total rate for the diamond
	if price_list_type == "Weight (in cts)":
		diamond.std_wt = range_det.get('std_wt')
		range_det['rate'] = rate # just in case if need to calculate amount after round off quantity(weight)
	diamond.total_diamond_rate = rate
	diamond.diamond_rate_for_specified_quantity = int(rate) * diamond.quantity # amount
	return int(rate) * diamond.quantity


def get_gemstone_rate(self):
	gemstone_amount = 0
	for stone in self.gemstone_detail:
		# Calculate the weight per piece
		stone.pcs = stone.pcs or 1
		gemstone_weight_per_pcs = stone.quantity / stone.pcs

		# Create filters for retrieving the Gemstone Price List
		filters = {
			"price_list": self.selling_price_list,
			"gemstone_type": stone.gemstone_type,
			"stone_shape": stone.stone_shape,
			"gemstone_quality": stone.gemstone_quality,
			"price_list_type": stone.price_list_type,
			"customer": self.customer,
			"cut_or_cab": stone.cut_or_cab,
		}
		if stone.price_list_type == "Weight (in cts)":
			filters.update(
				{
					"from_weight": ["<=", gemstone_weight_per_pcs],
					"to_weight": [">=", gemstone_weight_per_pcs],
				}
			)
		else:
			filters["gemstone_size"] = stone.gemstone_size

		# Retrieve the Gemstone Price List and calculate the rate
		gemstone_price_list = frappe.get_list(
			"Gemstone Price List",
			filters=filters,
			fields=["rate", "handling_rate"],
			order_by="effective_from desc",
			limit=1,
		)

		if not gemstone_price_list:
			frappe.msgprint(
				f"Gemstone Amount for {stone.gemstone_type} is 0\n Please Check if Gemstone Price Exists For {filters}"
			)
			return 0

		# Get Handling Rate of the Diamond if it is a cutomer provided Diamond
		rate = (
			gemstone_price_list[0].get("handling_rate")
			if stone.is_customer_item
			else gemstone_price_list[0].get("rate")
		)
		stone.total_gemstone_rate = rate
		stone.gemstone_rate_for_specified_quantity = int(rate) * stone.quantity
		gemstone_amount += int(rate) * stone.quantity
	return gemstone_amount


def get_making_charges(self):
	"""
	Calculates Making Charges IN BOM
	Takes BOM document as a parameter
	"""

	# If Customer Provided Metal/Finding, User will update the Making Rate Manually
	for metal in self.metal_detail:
		if metal.is_customer_item:
			metal.making_amount = metal.making_rate * metal.quantity

	for finding in self.finding_detail:
		if finding.is_customer_item:
			finding.making_amount = finding.making_rate * finding.quantity

	customer = self.customer
	item_details = frappe.db.get_value(
		"Item", self.item, ["item_subcategory", "setting_type"], as_dict=True
	)
	sub_category, setting_type = item_details.get("item_subcategory"), item_details.get(
		"setting_type"
	)
	metal_purity = self.metal_detail[0].get("metal_purity") if self.metal_detail else 0

	# Get Making Charge From Making Charge Price Master for mentioned Combinations
	making_charge_details = frappe.db.sql(
		"""
		SELECT 
		mcp.metal_purity,
		subcat.rate_per_gm,
		subcat.rate_per_pc,
		subcat.rate_per_gm_threshold,
		subcat.wastage
		FROM `tabMaking Charge Price` mcp
		LEFT JOIN `tabMaking Charge Price Item Subcategory` subcat
		ON subcat.parent = mcp.name
		WHERE 
		mcp.customer = '%s'
		AND subcat.subcategory = '%s'
		AND mcp.metal_purity = '%s'
		AND mcp.setting_type = '%s'
		"""
		% (customer, sub_category, metal_purity, setting_type),
		as_dict=True,
	)
	if making_charge_details:
		_set_total_making_charges(self, making_charge_details)

	amount = sum(flt(metal.making_amount) for metal in self.metal_detail)
	for finding in self.finding_detail:
		amount += flt(finding.making_amount)
	return amount


def _set_total_making_charges(self, making_charge_details):
	charges_details = {row.metal_purity:row for row in making_charge_details}
	# Unpack the making charge details
	# rate_per_gm, rate_per_pc, rate_per_gm_threshold, wastage = (
	#	 making_charge_details[0].get("rate_per_gm"),
	#	 making_charge_details[0].get("rate_per_pc"),
	#	 making_charge_details[0].get("rate_per_gm_threshold"),
	#	 making_charge_details[0].get("wastage"),
	# )

	# Calculate the total making charges
	# total_making_charges = (
	#	 rate_per_pc
	#	 if self.metal_and_finding_weight < rate_per_gm_threshold
	#	 else rate_per_gm * self.metal_and_finding_weight
	# )
	# total_making_charges += wastage * self.gold_bom_amount / 100

	# Calculate the making charges for each metal and finding
	for metal in self.metal_detail + self.finding_detail:
		making_charges = charges_details.get(metal.metal_purity) or {}
		if not metal.is_customer_item:
			# Set the rate per gram
			metal.making_rate = flt(making_charges.get("rate_per_gm"))

			# Calculate the making charges
			if self.metal_and_finding_weight < (making_charges.get("rate_per_gm_threshold") or 0):
				metal_making_charges = making_charges.get("rate_per_pc")
			else:
				metal_making_charges = metal.making_rate * metal.quantity

			# Set the making amount on the metal or finding
			metal.making_amount = metal_making_charges

			# Set wastage rate
			metal.wastage_rate = flt(making_charges.get("wastage"))

			# Add the wastage percentage to the making charges
			metal.wastage_amount = metal.wastage_rate * metal.amount / 100


def get_doctype_name(self):
	if "QTN" in self.name:
		return "Quotation"
	return "Sales Order" if "ORD" in self.name else None


def get_other_rate(self):
	self.igi_charges = self.igi_charges or 0
	self.dhc_charges = self.dhc_charges or 0
	self.sgl_charges = self.sgl_charges or 0
	self.hallmark_charges = self.hallmark_charges or 0
	other_details = [
		self.igi_charges,
		self.dhc_charges,
		self.sgl_charges,
		self.hallmark_charges,
	]
	return sum(other_details)


def prettify_filter(filters):
	prettified_filter = [
		f"{str(filter[1]).upper()} {str(filter[2]).upper()} {str(filter[3]).upper()}<br>"
		for filter in filters
	]
	return "".join(prettified_filter)


def set_bom_item_details(self):
	"""
	This method is called on Save of Quotation/Sales Order/ Sales Invoice before save
	This Functions checks if any specific modifications is provided in Quotation Items and updates BOM rate accordingly
	`self` parameter in this function is quotation/sales_order document.
	"""
	doctype = get_doctype_name(self)
	for item in self.items:
		remark = ""
		if item.diamond_quality:
			remark += f"Diamond Quality: {item.diamond_quality} \n"
		if item.colour:
			remark += f"Colour: {item.colour}"
		self = (
			frappe.get_doc("BOM", item.quotation_bom)
			if doctype == "Quotation"
			else frappe.get_doc("BOM", item.bom)
		)
		# Set Metal Details Fields
		for metal in self.metal_detail:
			if item.colour:
				metal.metal_colour = item.colour

		# Set Diamond Detail Fields
		for diamond in self.diamond_detail:
			set_diamond_fields(self, diamond, item)

		# Set Gemstone Fields
		for stone in self.gemstone_detail:
			set_gemstone_fields(stone, item)

		# Set Finding Fields
		for finding in self.finding_detail:
			if item.colour:
				finding.metal_colour = item.colour
		item.remarks = remark


def set_diamond_fields(self, diamond, item):
	doctype = get_doctype_name(self)
	customer = self.party_name if doctype == "Quotation" else self.customer
	if not item.diamond_grade:
		diamond_grade_1 = frappe.db.get_value(
			"Customer Diamond Grade",
			{"parent": customer, "diamond_quality": item.diamond_quality},
			"diamond_grade_1",
		)
		if diamond_grade_1:
			diamond.diamond_grade = diamond_grade_1
	else:
		diamond.diamond_grade = item.diamond_grade
	if item.diamond_quality:
		diamond.quality = item.diamond_quality
	self.save()
	return


def set_gemstone_fields(stone, item):
	if item.gemstone_type:
		stone.gemstone_type = item.gemstone_type
	if item.gemstone_quality:
		stone.gemstone_quality = item.gemstone_quality
	if item.gemstone_grade:
		stone.gemstone_grade = item.gemstone_grade
	if item.gemstone_cut_or_cab:
		stone.cut_or_cab = item.gemstone_cut_or_cab


def set_bom_rate_in_quotation(self):
	"""
	Fetch BOM Rates FROM BOM and replace the rate with BOM RATE
	"""
	for item in self.items:
		if item.quotation_bom:
			bom_doc = frappe.get_doc("BOM", item.quotation_bom)
			item.gold_bom_rate = bom_doc.gold_bom_amount
			item.diamond_bom_rate = bom_doc.diamond_bom_amount
			item.gemstone_bom_rate = bom_doc.gemstone_bom_amount
			item.other_bom_rate = bom_doc.other_bom_amount
			item.making_charge = bom_doc.making_charge
			item.bom_rate = bom_doc.total_bom_amount
			item.rate = bom_doc.total_bom_amount
			self.total = bom_doc.total_bom_amount
