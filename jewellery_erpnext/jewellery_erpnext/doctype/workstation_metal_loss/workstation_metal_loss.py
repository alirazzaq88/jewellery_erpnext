# Copyright (c) 2023, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WorkstationMetalLoss(Document):
	def before_save(self):
		self.update_gross_weights()

	def update_gross_weights(self):
		filters = [
			["Job Card", "workstation", "=", self.workstation],
			["Job Card", "modified", "Between", [self.date_from, self.date_to]],
			["Job Card","docstatus","=",1]
		]
		data = frappe.db.get_list('Job Card', filters=filters, fields=["name","loss_gold_weight", "loss_finding_weight", "metal_purity"])
		self.get_loss_by_purity(data)
		self.total_metal_loss = sum(i.get('loss_gold_weight') + j.get('loss_finding_weight') for i, j in zip(data, data))
		self.gold_loss = self.total_metal_loss - (self.loss_recovered or 0)

	def get_loss_by_purity(self, data):
		loss_by_purity = {}
		for loss in data:
			metal_purity = loss.get('metal_purity')
			loss_weight = loss.get('loss_gold_weight') + loss.get('loss_finding_weight')
			if metal_purity:
				if metal_purity in loss_by_purity:
					loss_by_purity[metal_purity] += loss_weight
				else:
					loss_by_purity[metal_purity] = loss_weight
		
		self.metal_loss_by_purity = []
		self.gross_pure_metal_loss = 0
		for metal_purity, metal_weight in loss_by_purity.items():
			try:
				pure_metal_loss = float(metal_weight) * float(metal_purity) / 100
			except Exception as e:
				pure_metal_loss = 0
			self.gross_pure_metal_loss += pure_metal_loss
			self.append('metal_loss_by_purity', {
				'metal_purity': metal_purity,
				'metal_weight': metal_weight,
				'pure_metal_weight': pure_metal_loss
			})