# Copyright (c) 2022, satya and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, get_link_to_form, getdate, new_line_sep, nowdate
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class MeltingLot(Document):
    def autoname(self):
        self.name = make_autoname(f"{self.product_purity}.###.")

    def validate(self):
        if self.order_details:
            for item in self.order_details:
                name,qty,production_qty,balance_production_qtys=frappe.db.get_value("Design Order Detail",{"parent":item.reference_name,"parenttype":item.reference_type,"item":item.item},['name','qty',"production_qty","balance_production_qty"])
                balance_qty=flt(qty-production_qty)
                item.remaining_qty=flt(balance_qty-item.production_qty) if flt(balance_qty-item.production_qty) >= 0 else 0
                balance_production_qty=flt(balance_qty-item.production_qty)
                # frappe.msgprint(str(balance_production_qty))
                # if qty != item.production_qty:
                #     if item.qty > balance_production_qty and  balance_production_qty >0:
                #         frappe.throw("Qty Should Not greater than Remaining Order Qty")
                if qty != production_qty:
                    if balance_production_qtys == balance_production_qty:
                        frappe.db.set_value("Design Order Detail",name,{"balance_production_qty":balance_production_qty,"production_qty":flt(production_qty)+flt(item.production_qty),"balance_ready_qty":qty})
                    elif balance_production_qtys != balance_production_qty:
                        frappe.db.set_value("Design Order Detail",name,{"balance_production_qty":balance_production_qty,"production_qty":flt(production_qty)+flt(item.production_qty),"balance_ready_qty":qty})
        if self.order_bunch_details:
            for item in self.order_bunch_details:
                get_id,weight,length,production_weight,production_length,balance_pro_len,balance_production_wei=frappe.db.get_value("Design Order Bunch Detail",{"parent":item.reference_name,"parenttype":item.reference_type,"item_code":item.item_code},["name","weight","length","production_weight","production_length","balance_production_length","balance_production_weight"])
                balance_length=flt(length-production_length)
                balance_weight=flt(weight-production_weight)
                item.remaining_weight=flt(balance_weight-item.production_weight) if flt(balance_weight-item.production_weight) >= 0 else 0
                item.remaining_length=flt(balance_length-item.production_length) if flt(balance_length-item.production_length) >= 0 else 0
                balance_production_weight=flt(balance_weight-item.production_weight)
                balance_production_length=flt(balance_length-item.production_length)
                # frappe.msgprint(str(balance_production_weight))
                # frappe.msgprint(str(balance_production_length))
                # if weight != item.production_weight:
                #     if item.weight > balance_production_weight and  balance_production_weight >0:
                #         frappe.throw("Qty Should Not greater than Remaining Order Qty")
                if weight != production_weight:
                    if balance_production_wei == balance_production_weight:
                        frappe.db.set_value("Design Order Bunch Detail",get_id,{"balance_production_weight":balance_production_weight,"production_weight":flt(production_weight)+flt(item.production_weight),"balance_ready_weight":weight})
                    elif balance_production_wei != balance_production_weight:
                        frappe.db.set_value("Design Order Bunch Detail",get_id,{"balance_production_weight":balance_production_weight,"production_weight":flt(production_weight)+flt(item.production_weight),"balance_ready_weight":weight})

                # if length != item.production_length:
                #     if item.length > balance_production_length and  balance_production_length > 0:
                #         frappe.throw("Qty Should Not greater than Remaining Order Qty")
                if length != production_length:
                    if balance_pro_len == balance_production_length:
                        frappe.db.set_value("Design Order Bunch Detail",get_id,{"balance_production_length":balance_production_length,"production_length":flt(production_length)+flt(item.production_length),"balance_ready_length":length})

                    elif balance_pro_len != balance_production_length:
                        frappe.db.set_value("Design Order Bunch Detail",get_id,{"balance_production_length":balance_production_length,"production_length":flt(production_length)+flt(item.production_length),"balance_ready_length":length})
	
    def on_submit(self):
        from jewellery_erpnext.jewellery_erpnext.doctype.operation_card.operation_card import make_operation_card
        make_operation_card(source_name=self.name)

@frappe.whitelist()
def make_melting_lot(source_name, target_doc=None):
	def update_qty(source, target, source_parent):
		if source.get("qty"):
			target.qty=source.get("qty")-source.get("production_qty")
			target.production_qty=source.get("qty")-source.get("production_qty")
			target.balance_production_qty=target.qty-target.production_qty
			target.balance_ready_qty=source.get("qty")-source.get("production_qty")
	
	def update_length_weight(source, target, source_parent):
		if source.get("length"):
			target.length=source.get("length")-source.get("production_length")
			target.production_length=source.get("length")-source.get("production_length")
			target.balance_production_length=target.length-target.production_length
			target.balance_ready_length=source.get("length")-source.get("production_length")
		if source.get("weight"):
			target.weight=source.get("weight")-source.get("production_weight")
			target.production_weight=source.get("weight")-source.get("production_weight")
			target.balance_production_weight=target.weight-target.production_weight
			target.balance_ready_weight=source.get("weight")-source.get("production_weight")
	doclist = get_mapped_doc(
		"Design Order",
		source_name,
		{
			"Design Order": {
				"doctype": "Melting Lot",
                "field_map": {
                    "purity": "product_purity"
                },
			},
			"Design Order Detail": {
				"doctype": "Melting Lot Design Order Detail",
                "field_map": {
                    "parent": "reference_name",
                    "parenttype":"reference_type"
                },
                "postprocess":update_qty,
				"condition": lambda doc: doc.production_qty <doc.qty
			},
            "Design Order Bunch Detail": {
				"doctype": "Melting Lot Design Order Bunch Detail",
                "field_map": {
                    "parent": "reference_name",
                    "parenttype":"reference_type"
                },
				"postprocess":update_length_weight,
				"condition": lambda doc: doc.production_length <doc.length or doc.production_weight < doc.weight,
			},
		},
		target_doc,
	)

	return doclist

