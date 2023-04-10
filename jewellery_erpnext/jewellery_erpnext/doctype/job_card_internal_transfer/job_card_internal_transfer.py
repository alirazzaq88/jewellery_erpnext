# Copyright (c) 2022, Nirali and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class JobCardInternalTransfer(Document):
	def validate(self):
		for row in self.items:
			if row.from_job_card:
				out_gold_weight = frappe.db.get_value('Job Card', row.from_job_card, 'out_gold_weight')
				out_finding_weight = frappe.db.get_value('Job Card', row.from_job_card, 'out_finding_weight')
				row.net_wt = flt(out_gold_weight) + flt(out_finding_weight)
