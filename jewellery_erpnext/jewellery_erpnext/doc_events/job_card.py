import frappe
from frappe import _
from frappe.utils import flt, get_link_to_form
from frappe.model.mapper import get_mapped_doc
from jewellery_erpnext.utils import get_variant_of_item


def onload(self,method):
	render_job_card_data(self)

def validate(self, method):
	if self.is_new():
		self.wip_warehouse = frappe.db.get_value("Operation Warehouse",{'parent': self.operation,'company': self.company},'warehouse')
	render_job_card_data(self)
	add_qc_params(self)

	# Set Employee and Workstation From Operations
	try:
		self.workstation = frappe.db.get_value("Operation", self.operation, 'workstation') or self.operation
		data = frappe.db.get_value("Workstation", self.workstation, ['workstation_type','employee'], as_dict=True)
		if data.get('workstation_type'):
			self.workstation_type = data.get('workstation_type')
		if not self.employee and data.get('employee'):
			self.append("employee",{'employee':data.get('employee'),'completed_qty':1})
	except Exception as e:
		pass

	# Set Wax Weigt In Tree Making And Casting Doctypes
	set_waxing_weight(self)

def set_waxing_weight(self):
	try:
		if self.operation == 'Waxing 1':
			frappe.db.set_value('Job Card', {'work_order': self.work_order, 'operation': 'Tree Making'}, 'wax_loss', self.wax_weight)
			frappe.db.set_value('Job Card', {'work_order': self.work_order, 'operation': 'Casting'}, 'wax_loss', self.wax_weight)
	except Exception as e:
		return

def onsubmit(self, method):
	if self.balance_gross != 0:
		return frappe.throw('Difference Between Total In Gross Weight And Total Out Gross Weight Should Be 0')
	if self.operation == "Tagging":
		if self.get("tag"):
			serial_no = create_serial_no(self)
			frappe.db.set_value("BOM",self.bom_no, "tag_no", serial_no)
		else:
			frappe.throw("Tag No. is missing")

def create_serial_no(self):
	doc = frappe.new_doc("Serial No")
	doc.serial_no = self.tag
	doc.item_code = self.item_code
	doc.purchase_document_type = self.doctype
	doc.purchase_document_no = self.name
	doc.purchase_date = frappe.utils.today()
	doc.purchase_time = frappe.utils.nowtime()
	doc.status = "Active"
	doc.save()
	return doc.name

def add_qc_params(self):
	if not self.item_code:
		return
	categories = frappe.db.get_value("Item",self.item_code,'item_category')
	params = frappe.db.sql_list(f"""select parameter from `tabQC Parameter` where (category is NULL or category = '{categories}') and (operation is NULL or operation ='{self.operation}')""")
	existing_params = [row.parameter for row in self.get("qc_details",[])]
	for entity in params:
		if entity not in existing_params:
			self.append("qc_details",{
				"parameter": entity,
			})

@frappe.whitelist()
def set_warehouse(operation, company):
	if operation:
		warehouse = frappe.get_all("Operation Warehouse",{'parent': operation,'company': company},'warehouse')
		if warehouse:
			# if len(warehouse) == 1:
			# 	wip_warehouse = warehouse[0].warehouse
			return warehouse
		
@frappe.whitelist()
def create_new_job_card(company,posting_date,for_quantity,work_order,bom_no,operation,workstation, employee):
	doc = frappe.new_doc("Job Card")
	doc.company = company
	doc.posting_date = posting_date
	doc.work_order = work_order
	doc.bom_no = bom_no
	doc.for_quantity = flt(for_quantity)
	doc.operation = operation
	# doc.employee = employee
	doc.wip_warehouse = (
		frappe.db.get_value(
			"Operation Warehouse",
			{'parent': operation, 'company': company},
			'warehouse',
		)
		or f"""All Warehouses - {frappe.db.get_value("Company", company, 'abbr')}"""
	)
	work_order_doc = frappe.get_doc('Work Order', work_order)
	oper_list = [operation.operation for operation in work_order_doc.operations]
	if operation not in oper_list:
		workstation = frappe.db.get_value('Operation', operation, 'workstation') or operation
		doc.workstation = workstation
		work_order_doc.append('operations', {
				'operation': operation,
				'workstation': workstation,
				'bom': work_order_doc.bom_no, 
				'time_in_mins': 1
			})
		work_order_doc.flags.ignore_validate_update_after_submit = True
		work_order_doc.save(ignore_permissions=True)
	doc.operation_row_number = frappe.db.get_value('Work Order Operation', {'parent': work_order_doc.name, 'operation':operation}, 'name')
	doc.save(ignore_permissions=True)
	return doc.name, doc.wip_warehouse

@frappe.whitelist()
def create_stock_entry(company,work_order,from_warehouse,to_warehouse,from_job_card,item_code,gross_wt,purity,net_wt,to_job_card=None,next_operation=None):
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Transfer for Manufacture"
	doc.company = company
	doc.work_order = work_order
	doc.from_warehouse = from_warehouse
	doc.to_warehouse = to_warehouse
	doc.from_job_card = from_job_card
	doc.to_job_card = to_job_card
	doc.append('items',{
		'item_code': item_code,
		'qty' : gross_wt,
		's_warehouse': from_warehouse,
		't_warehouse': to_warehouse,
		'next_operation': next_operation
	})
	doc.save(ignore_permissions=True)
	doc.submit()
	frappe.msgprint(_("Stock Entry {0} created").format(get_link_to_form("Stock Entry", doc.name)))

@frappe.whitelist()
def create_stock_entry_material_receipt(company,work_order,to_warehouse,from_job_card,item_code,gross_wt,purity,net_wt,to_job_card=None,next_operation=None):
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Receipt"
	doc.company = company
	doc.work_order = work_order
	# doc.from_warehouse = from_warehouse
	doc.to_warehouse = to_warehouse
	doc.from_job_card = from_job_card
	doc.to_job_card = to_job_card
	doc.append('items',{
		'item_code': item_code,
		'qty' : gross_wt,
		't_warehouse': to_warehouse,
		'next_operation': next_operation
	})
	doc.save(ignore_permissions=True)
	doc.submit()
	frappe.msgprint(_("Stock Entry {0} created").format(get_link_to_form("Stock Entry", doc.name)))

@frappe.whitelist()
def create_internal_transfer(company=None,item_code=None,gross_wt=None,purity=None,net_wt=None,work_order=None,from_job_card=None,to_job_card=None,to_combine_job_card=None,from_combine_job_card=None,next_operation=None, balance_gross=None):
	if balance_gross < gross_wt:
		return frappe.throw("Gross Weight Greater Than Balance Gross !")
	doc = frappe.new_doc("Job Card Internal Transfer")
	doc.company = company
	doc.work_order = work_order
	# doc.from_job_card = from_job_card
	# doc.to_job_card = to_job_card
	doc.append('items',{
		'item_code': item_code,
		'gross_wt' : gross_wt,
		'purity': purity,
		'net_wt': net_wt,
		'next_operation': next_operation,
		'from_job_card': from_job_card,
		'to_job_card': to_job_card,
		'from_combine_job_card': from_combine_job_card,
		'to_combine_job_card': to_combine_job_card
	})
	if to_job_card:
		frappe.db.set_value('Job Card', to_job_card, 'status', 'Work In Progress')
	doc.save(ignore_permissions=True)
	doc.submit()

	# Entry For Last Operation
	if not to_job_card and not to_combine_job_card:
		_delete_remaining_job_cards(work_order, from_job_card)
	frappe.msgprint(_("Job Card Out Weight {0} created").format(get_link_to_form("Job Card Internal Transfer", doc.name)))

def validate_out_weight(from_job_card, to_combine_job_card, gross_wt, balance_gross):
	if not from_job_card and not to_combine_job_card: return
	frappe.msgprint(str(balance_gross))

def _delete_remaining_job_cards(work_order, from_job_card):
	jc_list = frappe.db.get_list('Job Card', {'work_order': work_order, 'docstatus': 0, 'name': ("!=", from_job_card)}, ['name', 'operation'])
	for jc in jc_list:
		frappe.db.delete('Job Card', jc.get('name'))
		frappe.db.delete('Work Order Operation', {'parent': work_order, 'operation':jc.get('operation')})
	return

def render_job_card_data(self):
	set_reference_child_table_name(self)
	get_internal_in_weight(self)
	get_external_in_weight(self)
	get_out_weights(self)
	get_return_stock(self)
	set_wastages(self)
	get_last_out_weights(self)
	get_totals(self)
	
def set_reference_child_table_name(self):
	for item in self.items:
		if item.reference_doctype and item.reference_docname: return
		doctype = frappe.db.get_value('Work Order Item', {'parent': self.work_order, 'item_code':item.item_code}, 'reference_doctype')
		docname = frappe.db.get_value('Work Order Item', {'parent': self.work_order, 'item_code':item.item_code}, 'reference_docname')
		pcs = frappe.db.get_value('Work Order Item', {'parent': self.work_order, 'item_code':item.item_code}, 'pcs')
		item.reference_doctype = doctype
		item.reference_docname = docname
		item.pcs = pcs
		frappe.db.set_value('Job Card Item', item.name, 'reference_doctype', doctype)
		frappe.db.set_value('Job Card Item', item.name, 'reference_docname', docname)
		frappe.db.set_value('Job Card Item', item.name, 'pcs', pcs)
	frappe.db.commit()


def get_internal_in_weight(self):
	"""
		Render HTML Template For In Weights 
		Scenario 1: If Curent Job Card Is Not in Combine Job Card
			1a. Get In Weight From Previous Individual Job Card
			1b. Get In Weight From Previous Combined Job Card
		
		Scenario 2: If Curent Job Card Is in Combine Job Card
			2a. if Current Job Card Is In Combined Job Card and Previous Job Card is Not Combined.
			2b. if Current Job Card Is In Combined Job Card and Previous Job Card Is Combined Too 
	"""
	self.total_in_gross_weight = 0
	self.total_in_fine_weight = 0
	self.in_gold_weight = 0
	self.in_diamond_weight = 0
	self.in_gemstone_weight = 0
	self.in_finding_weight = 0
	self.in_other_weight = 0
	internal_in_weight_data = frappe.db.sql(f"""
		select jcit.item_code, jcit.from_job_card, jcit.to_job_card,jcit.from_combine_job_card,
						jcit.gross_wt, jcit.purity,  jcit.uom,
						(jc.out_gold_weight + jc.out_finding_weight - jc.balance_gross) as net_wt, jc.balance_gross
		from `tabJob Card Internal Transfer Item` jcit
		left join `tabJob Card` jc on jc.name = jcit.from_job_card
		where jcit.docstatus = 1 and jcit.to_job_card = '{self.name}' and (jcit.from_job_card IS NOT NUll or jcit.from_combine_job_card IS NOT NUll)
	""", as_dict= True)

	if internal_in_weight_data:
		if internal_in_weight_data[0].get('from_combine_job_card'):
			# 1b. Get In Weight From Previous Combined Job Card
			html_data = get_in_weights_from_prev_combined_jc(self, internal_in_weight_data)
		else:
			# 1a. Get In Weight From Previous Individual Job Card
			# set_internal_in_weight_fields(self, internal_in_weight_data)
			html_data = internal_in_weight_data
	else:
		html_data = _get_in_weights_from_combined_job_card(self)
	if html_data:
		for i in html_data:
			if i.get('net_wt'):
				i['net_wt'] = max(i['net_wt'], 0)
		set_internal_in_weight_fields(self, html_data)
		html_content = frappe.render_template(
								table_html, {"data": html_data, "table_type" : "Internal In Weight"})

		self.internal_in_weight_html = html_content

def _get_in_weights_from_combined_job_card(self):
	"""
		Check In Weight For Combined Job Cards
		Scenario 2a. if Current Job Card Is In Combined Job Card and Previous Job Card is Not Combined.
	"""
	if not self.in_combined_job_card: return
	cj_name = frappe.db.get_value('Combine Job Card Detail', {'job_card': self.name}, 'parent')
	if not cj_name: return
	cj_doc = frappe.get_doc('Combine Job Card', cj_name)
	job_card_list = tuple(row.job_card for row in cj_doc.details)
	internal_in_weight_data = frappe.db.sql(f"""
			select
			jcit.item_code, jcit.from_job_card, jcit.to_job_card,jcit.from_combine_job_card, jcit.to_combine_job_card,
							jcit.gross_wt as gross_wt, jcit.purity, (jc.out_gold_weight + jc.out_finding_weight - jc.balance_gross) as net_wt, 
							jc.balance_gross,
							jcit.uom
			from `tabJob Card Internal Transfer Item` jcit
			left join `tabJob Card` jc on jc.name =  jcit.from_job_card
			where jcit.docstatus = 1 and (jcit.to_job_card IN {job_card_list} or jcit.to_combine_job_card = '{cj_doc.name}') and (jcit.from_job_card IS NOT NULL or jcit.from_combine_job_card IS NOT NULL)
			and jc.work_order = '{self.work_order}'
		""", as_dict= True)
	return internal_in_weight_data or _get_in_weight_from_prev_combined_jc_self_in_cj(self) 
	
def _get_in_weight_from_prev_combined_jc_self_in_cj(self):
	"""
		Scenario 2b. if Current Job Card Is In Combined Job Card and Previous Job Card Is Combined Too 
	"""
	if not self.in_combined_job_card: return None
	cj_name = frappe.db.get_value('Combine Job Card Detail', {'job_card': self.name}, 'parent')
	if not cj_name: return None
	cj_doc = frappe.get_doc('Combine Job Card', cj_name)
	job_card_list = tuple(row.job_card for row in cj_doc.details)
	internal_in_weight_data = frappe.db.sql(f"""
		select jc.name,
		jcit.item_code, jc.name as from_job_card,
							jc.total_out_gross_weight as gross_wt, jcit.purity, jcit.uom,
							(jc.out_gold_weight + jc.out_finding_weight - jc.balance_gross) as net_wt,
							jc.balance_gross
	from `tabJob Card Internal Transfer Item` jcit
		left join `tabCombine Job Card` cjc on cjc.name =  jcit.from_combine_job_card
		left join `tabCombine Job Card Detail` cjcd on cjcd.parent = cjc.name
		left join `tabJob Card` jc on jc.name = cjcd.job_card 
			where jcit.docstatus = 1 and (jcit.to_job_card IN {job_card_list} or jcit.to_combine_job_card = '{cj_doc.name}') and (jcit.from_job_card IS NOT NULL or jcit.from_combine_job_card IS NOT NULL)
		and jc.work_order = '{self.work_order}'
	""", as_dict= True)
	return internal_in_weight_data or None


def get_in_weights_from_prev_combined_jc(self, internal_in_weight_data):
	data = []
	for i in internal_in_weight_data:
		cj_doc = frappe.get_doc('Combine Job Card', i.get('from_combine_job_card'))
		for jc in cj_doc.details:
			if frappe.db.get_value('Job Card', jc.get('job_card'), 'work_order') == self.work_order:
				balance_gross = frappe.db.get_value('Job Card', jc.get('job_card'), 'balance_gross')
				finding_weight = frappe.db.get_value('Job Card', jc.get('job_card'), 'out_finding_weight')
				net_wt = frappe.db.get_value('Job Card', jc.get('job_card'), 'out_gold_weight') + finding_weight - balance_gross
				data_dict = {'item_code': jc.get('production_item'), 
								'from_job_card': jc.get('job_card'), 
								'gross_wt': round(frappe.db.get_value('Job Card', jc.get('job_card'), 'out_gross_weight'), 3),
								'purity': i.get('purity'),
								'net_wt': round(net_wt, 3) if net_wt > 0 else 0,
								'balance_gross': round(balance_gross, 3)
							}
				data.append(data_dict)

	return data

def get_external_in_weight(self):
	"""
	Get all the Items From Stock Entry To Current Job Card
	"""
	external_in_weight_data = frappe.db.sql(f"""
		select item_code, from_job_card, to_job_card, s_warehouse as from_warehouse, t_warehouse as to_warehouse, 
		item_code, qty as gross_wt, metal_purity as purity, 0 as net_wt, uom, reference_doctype, reference_docname, pcs
		from `tabStock Entry Detail` where docstatus = 1 and to_job_card = '{self.name}' and (from_job_card = '' or from_job_card IS NULL)
	""", as_dict= True)
	if external_in_weight_data:
		metal_item = "M"
		diamond_item = "D"
		gemstone_item = "G"
		finding_item = "F"
		# in_gold_weight = in_diamond_weight = in_gemstone_weight = in_finding_weight = in_other_weight = 0
		for item in external_in_weight_data:
			variant_of = get_variant_of_item(item.get('item_code'))
			if variant_of in [metal_item, finding_item]:
				item.net_wt = item.get('gross_wt')
			else:
				item.net_wt = 0
		# Populate In Weight Fields In Job Card
		set_external_in_weight_fields(self, external_in_weight_data)

		# Render In Weight 
		html_content = frappe.render_template(
							table_html, {"data": external_in_weight_data, "table_type" : "External In Weight"})
		self.external_in_weight_html = html_content

def set_internal_in_weight_fields(self, internal_in_weight_data):
	total_weight = 0
	fine_weight = 0
	in_gold_weight = 0
	in_diamond_weight = 0
	in_gemstone_weight = 0
	in_finding_weight = 0
	in_other_weight = 0
	for item in internal_in_weight_data:
		if frappe.db.exists('Job Card', item.get('from_job_card')):
			jc_doc = frappe.get_doc('Job Card', item.get('from_job_card'))
			if jc_doc.docstatus != 1:
				jc_doc.save()
			in_gold_weight += jc_doc.out_gold_weight
			in_diamond_weight += jc_doc.out_diamond_weight
			in_gemstone_weight += jc_doc.out_gemstone_weight
			in_finding_weight += jc_doc.out_finding_weight
			in_other_weight += jc_doc.out_other_weight
			total_weight += item.get('gross_wt')
			fine_weight += item.get('net_wt') * item.get('purity') / 100
			self.wax_loss = jc_doc.wax_weight
	self.in_gold_weight = in_gold_weight
	self.in_diamond_weight = in_diamond_weight
	self.in_gemstone_weight = in_gemstone_weight
	self.in_finding_weight = in_finding_weight
	self.in_other_weight = in_other_weight
	self.total_in_gross_weight = total_weight
	self.total_in_fine_weight = fine_weight
	

def set_external_in_weight_fields(self, external_in_weight_data):
	total_out_weight = 0
	fine_weight = 0
	metal_item = "M"
	diamond_item = "D"
	gemstone_item = "G"
	finding_item = "F"
	for item in external_in_weight_data:
		fine_weight += item.get('net_wt') * float(item.get('purity') or 0) / 100
		variant_of = get_variant_of_item(item.get('item_code'))
		if variant_of == metal_item:
			total_out_weight += item.get('gross_wt')
			self.in_gold_weight += item.get('gross_wt')
		elif variant_of == diamond_item:
			total_out_weight += item.get('gross_wt') / 5
			self.in_diamond_weight += item.get('gross_wt')
		elif variant_of == gemstone_item:
			total_out_weight += item.get('gross_wt') / 5
			self.in_gemstone_weight += item.get('gross_wt')
		elif variant_of == finding_item:
			total_out_weight += item.get('gross_wt')
			self.in_finding_weight += item.get('gross_wt')
		else:
			total_out_weight += item.get('gross_wt')
			self.in_other_weight += item.get('gross_wt')
			
	self.total_in_gross_weight += total_out_weight
	self.total_in_fine_weight += fine_weight

def get_out_weights(self):
	self.out_gross_weight = 0
	self.total_out_fine_weight = 0
	out_weights_data = frappe.db.sql(f"""
		select jcit.item_code, jcit.from_job_card, jcit.to_job_card,
						jcit.gross_wt, jcit.purity, jcit.net_wt, jcit.uom,
						(jc.out_gold_weight - jc.balance_gross) as net_wt,
						jc.balance_gross
		from `tabJob Card Internal Transfer Item` jcit
		left join `tabJob Card` jc on jc.name = jcit.from_job_card
		where jcit.docstatus = 1 and jcit.from_job_card = '{self.name}' and (jcit.to_job_card IS NOT NUll or jcit.to_combine_job_card IS NOT NUll)
	""", as_dict= True)

	if out_weights_data:
		for i in out_weights_data:
			if i.get('net_wt'):
				i['net_wt'] = max(i['net_wt'], 0)
		_render_out_weights(self, out_weights_data)


def _render_out_weights(self, out_weights_data):
	# Set Out Weight Field
	out_weight = sum(item.get('gross_wt') for item in out_weights_data)
	out_fine_weight = sum((item.get('net_wt') * item.get('purity')/100) for item in out_weights_data)
	self.out_gross_weight = out_weight
	self.out_fine_weight = out_fine_weight
	self.total_out_fine_weight = out_fine_weight
	html_content = frappe.render_template(
						table_html, {"data": out_weights_data, "table_type" : "Out Weight"})

	self.out_weights_html = html_content

def get_return_stock(self):
	"""
		Render a table to show returned Stock to the store
	"""
	return_stock_html = frappe.db.sql(f"""
		select item_code, from_job_card, to_job_card, s_warehouse as from_warehouse, t_warehouse as to_warehouse, 
		item_code, qty as gross_wt, metal_purity as purity, 0 as net_wt, uom, pcs
		from `tabStock Entry Detail` where docstatus = 1 and from_job_card = '{self.name}' and (to_job_card = '' or to_job_card IS NULL)
	""", as_dict= True)
	self.return_balance = self.total_in_gross_weight - self.out_gross_weight
	if return_stock_html:
		html_content = frappe.render_template(
							table_html, {"data": return_stock_html, "table_type" : "External In Weight"})
		total_in = sum(i.get('required_qty')/5 for i in self.items)
		total_returned = sum(i.get('gross_wt')/5 for i in return_stock_html)
		self.return_balance = self.total_in_gross_weight - (self.out_gross_weight + total_returned) 
		self.returned_stock = html_content


def get_last_out_weights(self):
	"""
		Get Out Weights For Last Operation/Job Card
	"""
	out_weights_data = frappe.db.sql(f"""
		select item_code, from_job_card, to_job_card,
						gross_wt, purity, net_wt, uom
		from `tabJob Card Internal Transfer Item` where docstatus = 1 and from_job_card = '{self.name}' and (to_job_card IS NUll AND to_combine_job_card IS NUll)
	""", as_dict= True)
	if out_weights_data:
		# Set Out Weight Field
		out_weight = sum(item.get('gross_wt') for item in out_weights_data)
		out_fine_weight = sum((item.get('net_wt') * item.get('purity')/100) for item in out_weights_data)
		self.out_gross_weight = out_weight
		self.out_fine_weight = out_fine_weight 
		html_content = frappe.render_template(
							table_html, {"data": out_weights_data, "table_type" : "Out Weight"})

		self.out_weights_html = html_content

def get_wastages(self):
	"""
		Scenario 1: If Curent Job Card Is in Combine Job Card
			1a. if Current Job Card Is In Combined Job Card and Previous Job Card is Not Combined.
			1b. if Current Job Card Is In Combined Job Card and Previous Job Card Is Combined Too 
	"""
	cj_name = frappe.db.get_value('Combine Job Card Detail', {'job_card': self.name}, 'parent')
	if cj_name:
		cj_doc = frappe.get_doc('Combine Job Card', cj_name)
		job_card_list = tuple(row.job_card for row in cj_doc.details)
		query = f"""
			select
				jcit.item_code,
				SUM(jcit.gross_wt) as gross_wt
			from `tabJob Card Internal Transfer Item` jcit
			left join `tabJob Card` jc on jc.name = jcit.from_job_card
			where jcit.docstatus = 1
				and (jcit.to_job_card IN {job_card_list} or jcit.to_combine_job_card = '{cj_doc.name}')
				and (jcit.from_job_card IS NOT NULL or jcit.from_combine_job_card IS NOT NULL)
				and jc.work_order = '{self.work_order}'
			group by jcit.item_code
		"""
		internal_in_weight_data = frappe.db.sql(query, as_dict=True)
		if internal_in_weight_data:
			for scrap_item in cj_doc.scrap_items:
				scrap_items = self.get("scrap_items", {"item_code": scrap_item.get('item_code'), "parent": self.name})
				for data in internal_in_weight_data:
					if scrap_item.get('item_code') == data.get('item_code'):
						quantity = scrap_item.get('stock_qty') / cj_doc.total_in_gross_weight * data.get('gross_wt')
						if not scrap_items:
							self.append("scrap_items", {
								"doctype": "Job Card Scrap Item",
								"parent": self.name,
								"item_code": scrap_item.get('item_code'),
								"stock_qty": quantity
							})
						else:
							scrap_items[0].stock_qty = quantity


def set_wastages(self):
	if self.in_combined_job_card:
		get_wastages(self)
	
	# get_wastages_from_prev_combined_jc(self)
	# TODO: Wastages To be Fetched From Scrap Items
	metal_item = "M"
	diamond_item = "D"
	gemstone_item = "G"
	finding_item = "F"
	loss_gold_weight = 0
	loss_diamond_weight = 0
	loss_gemstone_weight = 0
	loss_finding_weight = 0
	for item in self.scrap_items:
		variant_of = get_variant_of_item(item.get('item_code'))
		if variant_of == metal_item:
			loss_gold_weight += item.get('stock_qty')
		elif variant_of == diamond_item:
			loss_diamond_weight += item.get('stock_qty')
		elif variant_of == gemstone_item:
			loss_gemstone_weight += item.get('stock_qty')
		elif variant_of == finding_item:
			loss_finding_weight += item.get('stock_qty')

	self.loss_gold_weight = loss_gold_weight
	self.loss_diamond_weight = loss_diamond_weight
	self.loss_gemstone_weight = loss_gemstone_weight
	self.loss_finding_weight = loss_finding_weight


def get_wastages_from_prev_combined_jc(self):
	internal_in_weight_data = frappe.db.sql(f"""
		select jcit.item_code, jcit.from_job_card, jcit.to_job_card,jcit.from_combine_job_card,
						jcit.gross_wt, jcit.purity, jcit.net_wt, jcit.uom
		
		from `tabJob Card Internal Transfer Item` jcit
		left join `tabCombine Job Card Detail` cjcd on cjcd.parent = jcit.from_combine_job_card
		left join `tabJob Card` jc on jc.name = cjcd.job_card
		where jcit.docstatus = 1 and jcit.to_job_card = '{self.name}' and (jcit.from_job_card IS NOT NUll or jcit.from_combine_job_card IS NOT NUll)
		and jc.work_order = '{self.work_order}'	
	""", as_dict= True)
	if internal_in_weight_data and internal_in_weight_data[0].get('from_combine_job_card'):
		cj_doc = frappe.get_doc('Combine Job Card', internal_in_weight_data[0].get('from_combine_job_card'))
		for scrap_item in cj_doc.scrap_items:
			scrap_items = self.get("scrap_items", {"item_code": scrap_item.get('item_code'), "parent": self.name})
			quantity = scrap_item.get('stock_qty')/cj_doc.total_in_gross_weight * internal_in_weight_data[0].get('gross_wt')
			if not scrap_items:
				self.append("scrap_items", {
					"doctype": "Job Card Scrap Item",
					"parent": self.name,
					"item_code": scrap_item.get('item_code'),
					"stock_qty": quantity			
				})
			else:
				scrap_items[0].stock_qty = quantity	
	

def get_totals(self):
	internal_in_weights = frappe.db.sql(f"""
		select IFNULL(sum(gross_wt), 0) as internal_in_gross_wt, IFNULL(sum(net_wt), 0) as internal_in_net_wt
		from `tabJob Card Internal Transfer Item` where docstatus = 1 and to_job_card = '{self.name}' and (from_job_card IS NOT NUll or from_combine_job_card IS NOT NUll)
	""", as_dict= True)

	# set_total_in_weight_fields(self, internal_in_weights[0]['internal_in_gross_wt'])
	set_total_out_weight_fields(self)
	self.balance_gross = self.total_in_gross_weight - self.total_out_gross_weight
	self.balance_gross = round(self.balance_gross, 3)

	total_wastage = self.loss_gold_weight + self.loss_diamond_weight/5 + self.loss_gemstone_weight/5 + self.loss_finding_weight
	fine_wastage = (self.loss_gold_weight + self.loss_finding_weight) * (float(self.metal_purity or 0) / 100)
	self.total_out_fine_weight = self.out_fine_weight + fine_wastage
	self.balance_fine = self.total_in_fine_weight - self.total_out_fine_weight 
	self.balance_fine = round(self.balance_fine, 3)
	total_wastage = round(total_wastage, 3)
	
	html_content = frappe.render_template(
							total_html, {"total_in_gross_weight" : round(self.total_in_gross_weight, 3),
														"total_out_gross_weight" : round(self.out_gross_weight, 3),
														"wastages": total_wastage,
														"fine_wastages": fine_wastage,
														"balance": round(self.balance_gross, 3),
														"balance_fine":round(self.balance_fine, 3),
														"total_in_fine_weight" : round(self.total_in_fine_weight, 3),
														"total_out_fine_weight" : round(self.out_fine_weight, 3),
														})
	self.total_html = html_content


def set_total_in_weight_fields(self, internal_in_gross_wt):
	internal_in_gross_wt = self.in_gold_weight + self.in_diamond_weight/5 + self.in_gemstone_weight/5 + self.in_finding_weight + self.in_other_weight
	# self.total_in_gross_weight = internal_in_gross_wt + external_in_gross_wt - self.in_other_weight
	# self.total_in_gross_weight = internal_in_gross_wt 
	#TODO: Total In Fine Weight

def set_total_out_weight_fields(self):
	wastage_loss = self.loss_gold_weight + self.loss_diamond_weight/5 + self.loss_gemstone_weight/5 + self.loss_finding_weight
	self.out_gold_weight = self.in_gold_weight - self.loss_gold_weight
	self.out_diamond_weight = self.in_diamond_weight - self.loss_diamond_weight
	self.out_gemstone_weight = self.in_gemstone_weight - self.loss_gemstone_weight
	self.out_finding_weight = self.in_finding_weight - self.loss_finding_weight
	self.out_other_weight = self.in_other_weight - self.loss_other_weight
	if self.in_combined_job_card:
		self.out_gross_weight = self.out_gold_weight + (self.in_diamond_weight/5 - self.loss_diamond_weight/5) + (self.in_gemstone_weight/5 - self.loss_gemstone_weight/5) + self.out_finding_weight + self.out_other_weight
	self.total_out_gross_weight = self.out_gross_weight + wastage_loss
	self.total_out_fine_weight = (self.out_fine_weight + (self.loss_gold_weight + self.loss_finding_weight)) * (float(self.metal_purity or 0) / 100)



@frappe.whitelist()
def stock_entry_detail(item):
	job_card = frappe.get_doc("Job Card", item)
	stock_entry_detail = frappe.db.sql(f"""
				select jc.name,sed.item_code, sed.item_name, jc.work_order, 
				sed.qty- ifnull(jcsi.stock_qty,0) as "gross_wgt",
				 sed.metal_purity as purity, sed.uom,
				sed.reference_doctype,
				sed.reference_docname,
				sed.pcs
				from `tabJob Card` jc
				left join `tabStock Entry` se on se.work_order = jc.work_order
				left join `tabStock Entry Detail` sed on sed.parent = se.name
			    left join `tabJob Card Scrap Item` jcsi on jcsi.parent = jc.name and jcsi.item_code = sed.item_code
				where jc.name = '{item}' and se.stock_entry_type != "Manufacture" and se.docstatus = 1
				AND se.is_returned = 0
				""", as_dict = True)

			
	html_content_stock_entry = frappe.render_template(
							table_stock_entry, {"data": stock_entry_detail, "table_type" : "Stock Entry Detail"})
	frappe.msgprint(str(html_content_stock_entry))
	if job_card.scrap_items:
		scrap_item = frappe.db.sql(f"""
			select  jc.name,jcst.item_code, jcst.stock_qty, jcst.stock_uom
			from `tabJob Card` jc
			left join `tabJob Card Scrap Item` jcst on jcst.parent = jc.name
			where jc.name = '{item}' """, as_dict = True)
		html_content_scrap_item= frappe.render_template(
							table_scrap_item, {"data": scrap_item, "table_type" : "Scarp Item"})
		frappe.msgprint(str(html_content_scrap_item))

		
table_html = """
<table class="table table-bordered table-hover" width='100%' style="border: 1px solid #d1d8dd;border-collapse: collapse;">
<thead>
	<tr>
		<th style="border: 1px solid #d1d8dd; font-size: 11px;">Item Code</th>
		{% if table_type == 'Internal In Weight' %}
			<th style="border: 1px solid #d1d8dd; font-size: 11px;">Job Card</th>
		{% elif table_type == 'External In Weight' %}
			<th style="border: 1px solid #d1d8dd; font-size: 11px;">Warehouse</th>
			<th style="border: 1px solid #d1d8dd; font-size: 11px;">Pcs</th>
		{% elif table_type == 'Out Weight' %}
			<th style="border: 1px solid #d1d8dd; font-size: 11px;">Job Card</th>
		{% elif table_type == 'Wastage Weight' %}
			<th style="border: 1px solid #d1d8dd; font-size: 11px;">To Warehouse</th>
		{% endif %}
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Gross Wt</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Purity</th>
		{% if table_type != 'External In Weight' %}
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Net Wt</th>
		<th style="border: 1px solid #d1d8dd; font-size: 11px;">Balance Gross</th>
		{% endif %}
		
	</tr>
</thead>
<tbody>
{% for item in data %}
	<tr>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.item_code }}</td>
		{% if table_type == 'Internal In Weight' %}
			<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.from_job_card or '' }}</td>
		{% elif table_type == 'External In Weight' %}
			<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.from_warehouse or '' }}</td>
			<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.pcs or '' }}</td>
		{% elif table_type == 'Out Weight' %}	
			<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.to_job_card or '' }}</td>
		{% elif table_type == 'Wastage Weight' %}
			<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.to_warehouse or '' }}</td>
		{% endif %}
		<script type='text/javascript'>
			function stock_entry(job_card){
				frappe.call({
					method:"jewellery_erpnext.jewellery_erpnext.doc_events.job_card.stock_entry_detail",
					args:{
						'item':job_card
					},
					callback: function(r) {
					}
					});
			}
		</script>
		{% if table_type == 'Internal In Weight' %}
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem" onclick=stock_entry('{{item.from_job_card}}')>{{ item.gross_wt }} {{ item.uom or '' }}</td>
		{% else %}
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.gross_wt }} {{ item.uom or '' }}</td>
		{% endif %}
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.purity }}</td>
		{% if table_type != 'External In Weight' %}
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.net_wt }}</td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.balance_gross }}</td>
		{% endif %}
		
	</tr>
{% endfor %}
</tbody>
</table>
"""
table_stock_entry = """
<table class="table table-bordered table-hover" width='100%' style="border: 1px solid #d1d8dd;border-collapse: collapse;">
<thead>
	<tr>
		<th style="border: 1px solid #d1d8dd; font-size: 11px;">Item Code</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Item Name</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Gross Wgt</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Purity</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Pcs</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">UOM</th>
	</tr>
</thead>
<tbody>
{% for item in data %}
	<tr>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.item_code }}</td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.item_name}} </td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.gross_wgt}} </td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.purity}} </td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.pcs}} </td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.uom}} </td>
	</tr>
{% endfor %}
</tbody>
</table>
"""
table_scrap_item = """
<table class="table table-bordered table-hover" width='100%' style="border: 1px solid #d1d8dd;border-collapse: collapse;">
<thead>
	<tr>
		<th style="border: 1px solid #d1d8dd; font-size: 11px;">Item Code</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Stock Qty</th>
		<th style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;">Stock UOM</th>
	</tr>
</thead>
<tbody>
{% for item in data %}
	<tr>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.item_code }}</td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.stock_qty}} </td>
		<td style="text-align:end;border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">{{ item.stock_uom}} </td>
	</tr>
{% endfor %}
</tbody>
</table>
"""



total_html = """
<table class="table table-hover" width='100%'  style="border: 1px solid #d1d8dd;border-collapse: collapse;">
<tbody>
	

	<tr>
				<th style="border: 1px solid #d1d8dd;font-size: 11px;"></th>
				<th style="border: 1px solid #d1d8dd;font-size: 11px;">Gross</th>
				<th  style="border: 1px solid #d1d8dd;font-size: 11px;">Fine</th>
		</tr>
	

	 <tr>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">In</th>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ total_in_gross_weight}}</td>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ total_in_fine_weight }}</td>
		 </tr>

	<tr>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">Out</th>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ total_out_gross_weight }}</td>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ total_out_fine_weight }}</td>
		</tr>
	
	<tr>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem">Wastage</th>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ wastages }}</td>
				<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end">{{ fine_wastages }}</td>
			</tr>
	
	<tr>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem"><b>Balance</b></td>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end"><b>{{ balance }}<b></td>
		<td style="border: 1px solid #d1d8dd; font-size: 11px;padding:0.25rem;text-align:end"><b>{{ balance_fine }}<b></td>
	</tr>
</tbody>
</table>
"""

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_item(source, target, source_parent):
		if not target.conversion_factor:
			target.conversion_factor = 1

		pending_rm_qty = flt(source.required_qty) - flt(source.transferred_qty)
		if pending_rm_qty > 0:
			target.qty = pending_rm_qty

	def set_missing_values(source, target):
		target.purpose = "Material Transfer for Manufacture"
		target.from_bom = 1
		# change
		target.from_job_card = ''

		# avoid negative 'For Quantity'
		pending_fg_qty = flt(source.get("for_quantity", 0)) - flt(source.get("transferred_qty", 0))
		target.fg_completed_qty = max(pending_fg_qty, 0)

		target.set_transfer_qty()
		target.calculate_rate_and_amount()
		target.set_missing_values()
		target.set_stock_entry_type()

		wo_allows_alternate_item = frappe.db.get_value(
			"Work Order", target.work_order, "allow_alternative_item"
		)
		for item in target.items:
			item.allow_alternative_item = int(
				wo_allows_alternate_item
				and frappe.get_cached_value("Item", item.item_code, "allow_alternative_item")
			)
		target.to_warehouse = frappe.db.get_value('Work Order', source.work_order, 'wip_warehouse')

	doclist = get_mapped_doc(
		"Job Card",
		source_name,
		{
			"Job Card": {
				"doctype": "Stock Entry",
				"field_map": {"name": "job_card", "for_quantity": "fg_completed_qty"},
			},
			"Job Card Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {
					"source_warehouse": "s_warehouse",
					"required_qty": "qty",
					"name": "job_card_item",
					"reference_doctype": "reference_doctype",
					"reference_docname": "reference_docname",
					"pcs": "pcs"
				},
				"postprocess": update_item,
				"condition": lambda doc: doc.required_qty > 0 and doc.transferred_qty < doc.required_qty,
			},
		},
		target_doc,
		set_missing_values,
	)
	
	return doclist


@frappe.whitelist()
def make_stock_return(source_name, target_doc=None):
	"""
		Create Stock Return Entry.
	"""
	def update_item(source, target, source_parent):
		target.to_warehouse = frappe.db.get_value('Work Order', source_parent.work_order, 'wip_warehouse')

		if not target.conversion_factor:
			target.conversion_factor = 1

		pending_rm_qty = flt(source.required_qty) - flt(source.transferred_qty)
		if pending_rm_qty > 0:
			target.qty = pending_rm_qty

	def set_missing_values(source, target):
		target.purpose = "Material Transfer for Manufacture"
		target.from_bom = 1
		# change
		# target.from_job_card = ''
		target.to_job_card = ''
		target.is_returned = True
		# target.is_return = True
		# avoid negative 'For Quantity'
		pending_fg_qty = flt(source.get("for_quantity", 0)) - flt(source.get("transferred_qty", 0))
		target.fg_completed_qty = max(pending_fg_qty, 0)

		target.set_transfer_qty()
		target.calculate_rate_and_amount()
		target.set_missing_values()
		target.set_stock_entry_type()

		wo_allows_alternate_item = frappe.db.get_value(
			"Work Order", target.work_order, "allow_alternative_item"
		)
		target.items = []
		# for item in target.items:
		# 	item.allow_alternative_item = int(
		# 		wo_allows_alternate_item
		# 		and frappe.get_cached_value("Item", item.item_code, "allow_alternative_item")
		# 	)

	doclist = get_mapped_doc(
		"Job Card",
		source_name,
		{
			"Job Card": {
				"doctype": "Stock Entry",
				"field_map": {"name": "job_card", "for_quantity": "fg_completed_qty"},
			},
			"Job Card Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {
					"source_warehouse": "s_warehouse",
					"required_qty": "qty",
					"name": "job_card_item",
					"reference_doctype": "reference_doctype",
					"reference_docname": "reference_docname",
					"pcs": "pcs",
				},
				"postprocess": update_item,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist

# def calculate_total(self):
# 	self.total_in_gross_weight = flt(sum([row.gross_wt for row in self.internal_in_weight]))

# 	total_internal_net_weight = flt(sum([row.net_wt for row in self.internal_in_weight]))
# 	total_external_net_weight = flt(sum([row.net_wt for row in self.external_in_weight]))
# 	self.total_in_fine_weight = total_internal_net_weight + total_external_net_weight

# 	total_out_gross_weight = flt(sum([row.gross_wt for row in self.out_weights]))
# 	total_wastage_gross_weight = flt(sum([row.gross_wt for row in self.wastages]))
# 	self.total_out_gross_weight = total_out_gross_weight + total_wastage_gross_weight

# 	total_out_net_weight = flt(sum([row.net_wt for row in self.out_weights]))
# 	total_wastage_net_weight = flt(sum([row.net_wt for row in self.wastages]))
# 	self.total_out_fine_weight = total_out_net_weight + total_wastage_net_weight

# 	self.balance_gross =  self.total_in_gross_weight - total_out_gross_weight
# 	self.balance_fine = self.total_in_fine_weight - total_out_fine_weight


@frappe.whitelist()
def make_additional_stock_entry(source_name, target_doc=None):
	def update_item(source, target, source_parent):
		target.to_warehouse = frappe.db.get_value('Work Order', source_parent.work_order, 'wip_warehouse')

		if not target.conversion_factor:
			target.conversion_factor = 1

		pending_rm_qty = flt(source.required_qty) - flt(source.transferred_qty)
		if pending_rm_qty > 0:
			target.qty = pending_rm_qty

	def set_missing_values(source, target):
		target.purpose = "Material Transfer for Manufacture"
		target.from_bom = 1

		# avoid negative 'For Quantity'
		pending_fg_qty = flt(source.get("for_quantity", 0)) - flt(source.get("transferred_qty", 0))
		target.fg_completed_qty = max(pending_fg_qty, 0)

		target.set_missing_values()
		target.set_stock_entry_type()
		target.from_job_card = ''
		wo_allows_alternate_item = frappe.db.get_value(
			"Work Order", target.work_order, "allow_alternative_item"
		)
		target.items = []
		# for item in target.items:
		# 	item.allow_alternative_item = int(
		# 		wo_allows_alternate_item
		# 		and frappe.get_cached_value("Item", item.item_code, "allow_alternative_item")
		# 	)

	doclist = get_mapped_doc(
		"Job Card",
		source_name,
		{
			"Job Card": {
				"doctype": "Stock Entry",
				"field_map": {"name": "job_card", "for_quantity": "fg_completed_qty"},
			},
			"Job Card Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {
					"source_warehouse": "s_warehouse",
					"required_qty": "qty",
					"name": "job_card_item",
				},
				"postprocess": update_item,
				"condition": lambda doc: doc.required_qty > 0,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist
