# Copyright (c) 2022, satya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import make_autoname
from frappe.model.document import Document

class DesignOrder(Document):
	def autoname(self):
		self.name = make_autoname(f"DO.###")
