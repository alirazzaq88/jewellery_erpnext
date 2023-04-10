# Copyright (c) 2022, satya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ParentMeltingLot(Document):
    def autoname(self):
        self.name = make_autoname(f"P-{self.product_purity}.{self.product_abbr}.###.")
