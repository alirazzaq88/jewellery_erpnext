# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form
from frappe.model.mapper import get_mapped_doc

class OperationCard(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		if self.production_order:
			key= f"{self.production_order}/"
		else:
			key = f"{self.slip}/"

		self.name = make_autoname(key=key, doc=self)

	def onload(self):
		self.render_job_card_data()


	def render_job_card_data(self):
		"""
			Get all the Items From Stock Entry To Current Operation Card
		"""
		# Render External In Weight
		external_in_weight_data = self.get_external_in_weight()
		html_content = frappe.render_template(
								table_html, {"data": external_in_weight_data, "table_type" : "External In Weight"})
		self.external_in_weights = html_content

		# Render Wastage Weight
		loss_data = self.get_loss_weight()
		html_content = frappe.render_template(
								table_html, {"data": loss_data, "table_type" : "External In Weight"})
		self.loss_broken = html_content

	def get_external_in_weight(self):
		warehouse = frappe.db.get_value('Operation Warehouse', {'parent': self.operation}, 'warehouse')
		return frappe.db.sql(f"""
			select parent, item_code, s_warehouse as from_warehouse, t_warehouse as to_warehouse, 
			item_code, qty as gross_wt, metal_purity as purity, 0 as net_wt, uom
			from `tabStock Entry Detail` where docstatus = 1 and t_warehouse = '{warehouse}'
			and operation_card = '{self.name}' 
		""", as_dict= True)
	
	def get_loss_weight(self):
		warehouse = frappe.db.get_value('Operation Warehouse', {'parent': self.operation}, 'warehouse')
		return frappe.db.sql(f"""
			select sed.parent, sed.item_code, sed.s_warehouse as from_warehouse, sed.t_warehouse as to_warehouse, 
			sed.item_code, sed.qty as gross_wt, sed.metal_purity as purity, 0 as net_wt, sed.uom
			from `tabStock Entry Detail` sed
			join `tabStock Entry` se ON se.name = sed.parent
			where sed.docstatus = 1 and sed.s_warehouse = '{warehouse}'
			and sed.operation_card = '{self.name}'
			and se.stock_entry_type = 'Broken / Loss'
		""", as_dict= True)

	
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


@frappe.whitelist()
def make_stock_return(source_name, target_doc=None):
	"""
		Create Stock Return Entry.
	"""
	# warehouse = frappe.db.get_value('Operation Warehouse', {'parent': source_name}, 'warehouse')
	warehouse_details = frappe.db.sql(f"""
				SELECT opw.warehouse
				FROM `tabOperation Warehouse` opw 
				JOIN `tabOperation Card` oc ON oc.operation = opw.parent
				WHERE oc.name = '{source_name}' 
	""", as_dict=True)

	warehouse = warehouse_details[0].get('warehouse') if warehouse_details else None

	def set_missing_values(source, target):
		target.stock_entry_type = 'Broken / Loss'
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
def make_operation_card_transfer(operation, operation_card):
	# Make Operation Card For Next Operation
	new_oct = frappe.new_doc('Operation Card Transfer')
	new_oct.operation_card = operation_card
	new_oct.next_operation = operation
	new_oct.save()
	frappe.msgprint(("Operation Card Transfer {0} created").format(get_link_to_form("Operation Card Transfer", new_oct.name)))