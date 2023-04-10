import frappe

def autoname(self, method = None):
		self.naming_series = 'M/.{code}./.{category_code}.-.{item_code}./.####'
        
def validate(self, method = None):
    mould  = self.name.split('-') 
    # mould_no = mould[0] +"/"+ self.name.split("/",3)[3]
    mould_no = mould[0] +"/"+ self.name.rsplit('/', 1)[-1]
    self.mould_no = mould_no
    item = frappe.get_doc("Item",self.item_code)
    item.mould = self.mould_no
    item.save()