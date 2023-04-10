import frappe

def validate(self, method):
	create_attribute_value(self)

def create_attribute_value(self):
	for row in self.item_attribute_values:
		row.value = row.attribute_value
		if not frappe.db.exists("Attribute Value",row.attribute_value):
			doc = frappe.new_doc("Attribute Value")
			doc.attribute_value = row.attribute_value
			doc.save()
