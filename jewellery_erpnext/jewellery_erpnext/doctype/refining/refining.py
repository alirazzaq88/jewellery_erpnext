import frappe
from frappe.utils import flt
from frappe.model.document import Document


class Refining(Document):
    def validate(self):
        self.check_overlap()
        self.update_metal_loss()
        self.set_fine_weight()

    def set_fine_weight(self):
        self.fine_weight = flt(self.refining_gold_weight) * flt(self.purity) / 100

    def on_submit(self):
        self.update_metal_loss(update=True)
        material_receipt = make_material_receipt(self.fine_weight)
        frappe.db.set_value(self.doctype, self.name, "material_receipt", material_receipt)
        self.reload()

    def on_cancel(self):
        self.update_metal_loss(revert=True)
        if self.material_receipt:
            frappe.get_doc("Stock Entry",self.material_receipt).cancel()

    def check_overlap(self):
        if not self.multi_operation:
            condition = f"""docstatus != 2 and dustname = '{self.dustname}' and multi_operation = {self.multi_operation} 
                    and operation = '{self.operation}' and employee = '{self.employee}' and (
					(('{self.date_from}' > date_from) and ('{self.date_from}' < date_to))
					or (('{self.date_to}' > date_from) and ('{self.date_to}' < date_to))
					or (('{self.date_from}' <= date_from) and ('{self.date_to}' >= date_to))
				)"""
            name = frappe.db.sql(
                f"select name from `tabRefining` where name != '{self.name}' and {condition}"
            )
            if name:
                frappe.throw(
                    f"Document is overlapping with <b><a href='/app/refining/{name[0][0]}'>{name[0][0]}</a></b>"
                )
        else:
            if not self.refining_operation_details:
                return
            operation = [
                frappe.db.escape(row.operation)
                for row in self.refining_operation_details
            ]
            condition = f"""r.docstatus != 2 and dustname = '{self.dustname}' and r.multi_operation = {self.multi_operation} and 
                    ro.operation in ({', '.join(operation)}) and ((('{self.date_from}' >= r.date_from) and ('{self.date_from}' <= r.date_to))
					or (('{self.date_to}' >= r.date_from) and ('{self.date_to}' <= r.date_to))
					or (('{self.date_from}' <= r.date_from) and ('{self.date_to}' >= r.date_to))
				)"""
            name = frappe.db.sql(
                f"""select r.name from `tabRefining` r, `tabRefining Operation Detail` ro where 
									r.name = ro.parent and r.name != '{self.name}' and {condition}"""
            )
            if name:
                frappe.throw(
                    f"Document is overlapping with <b><a href='/app/refining/{name[0][0]}'>{name[0][0]}</b>"
                )

    def update_metal_loss(self, update=False, revert=False):
        if self.multi_operation:
            operations = []
            ratio = {}
            for row in self.refining_operation_details:
                operations.append(row.operation)
                ratio.update({row.operation:flt(row.ratio)/100})

            omls = frappe.db.get_values(
                "Operation Metal Loss",
                {
                    "operation": ["in", operations],
                    "date_from": ["<=", self.date_from],
                    "date_to": [">=", self.date_to],
                },
                ["name","loss_recovered","gross_pure_metal_loss", "operation"],
                as_dict=1
            )
            gross_pure_metal_loss = sum(oml.get("gross_pure_metal_loss", 0) for oml in omls)
            op = set(operations).difference(set([op.get("operation") for op in omls]))
            if op:
                print_msg(f"No Operation Metal Loss found for <b>{', '.join(op)}</b>",update)

            total_ratio = sum(value for value in ratio.values())
            for oml in omls:
                if not ratio[oml.get("operation")] or total_ratio != 1:
                    ratio[oml.get("operation")] = flt(oml.get("gross_pure_metal_loss") / gross_pure_metal_loss, 3)
                fine_weight = flt(self.fine_weight) * ratio[oml.get("operation")]
                if oml.get("gross_pure_metal_loss", 0) < fine_weight:
                    print_msg(f"Calculated loss recovered({fine_weight}) is greater than Total metal loss({oml.get('gross_pure_metal_loss')}).",update)
                
                if revert:
                    loss_recovered = oml.get("loss_recovered") - fine_weight
                else:
                    loss_recovered = oml.get("loss_recovered") + fine_weight
                if update or revert:
                    self.add_to_child("Operation Metal Loss", oml.name, fine_weight, update=update, revert=revert)
                    gold_loss = oml.get("gross_pure_metal_loss") - loss_recovered
                    frappe.db.set_value(
                        "Operation Metal Loss",
                        oml.name,
                        {"loss_recovered": loss_recovered, "gold_loss": gold_loss},
                    )
                # for employees against each opertion
                self.update_multi_emp_against_operation(oml.get('operation'), fine_weight, update, revert)
            
            # update ratio in table
            for row in self.refining_operation_details:
                row.ratio = ratio[row.operation] * 100          
        else:
            # for single operation
            self.update_single_metal_loss("operation", update, revert)
            # with single employee
            if self.employee:
                self.update_single_metal_loss("employee", update, revert)
            else:
                # with multiple employees
                self.update_multi_emp_against_operation(self.operation, self.fine_weight, update, revert)


    def update_single_metal_loss(self, rtype, update=False, revert=False):
        filters = {
            rtype: self.get(rtype),
            "date_from": ["<=", self.date_from],
            "date_to": [">=", self.date_to],
            "docstatus": ["!=",2]
        }
        or_filters = None
        extra_column = []
        if rtype == "operation":
            doctype = "Operation Metal Loss"
        else:
            doctype = "Employee Metal Loss"
            if revert:
                filters["dust_added"]= ['like', f'%{self.dustname}%']
            else:
                or_filters = {"dust_added": ["is","NULL"], "dust_added": ['not like', f'%{self.dustname}%']}
            extra_column.append('dust_added')
        ml = frappe.get_list(
            doctype,
            filters,
            ["name", "gross_pure_metal_loss", "loss_recovered"] + extra_column,
            or_filters=or_filters
        )
        if ml:
            ml = ml[0]
            if ml.get("gross_pure_metal_loss", 0) < flt(self.fine_weight):
                print_msg(
                    f"Fine Weight is greater than Total metal loss({ml.get('gross_pure_metal_loss')}).", update
                )
            dusts =(ml.get('dust_added') or '') + self.dustname + ', '
            if revert:
                dusts = ml.get('dust_added','').replace(f'{self.dustname}, ', '')
                loss_recovered = ml.get("loss_recovered") - flt(self.fine_weight)
            else:
                loss_recovered = ml.get("loss_recovered", 0) + flt(self.fine_weight)
            if update or revert:
                self.add_to_child(doctype, ml.name, flt(self.fine_weight), update=update, revert=revert)
                gold_loss = ml.get("gross_pure_metal_loss") - loss_recovered
                values = {"loss_recovered": loss_recovered, "gold_loss": gold_loss}
                if rtype == 'employee':
                    values['dust_added'] = dusts
                frappe.db.set_value(
                    doctype,
                    ml.name,
                    values
                )
        else:
            msg = f"No {doctype} found for <b>{self.get(rtype)}</b> in selected date range"
            print_msg(msg, update)

    def update_multi_emp_against_operation(self, operation, fine_weight, update, revert):
        if not fine_weight:
            return
        employees = frappe.db.get_values(
            "Job Card",
            {
                "operation": operation,
                "posting_date": ["between", [self.date_from, self.date_to]],
                "employee_1": ["!=",None],
                "loss_gold_weight": [">",0]
            },
            "employee_1",
            pluck=1,
            distinct=1,
        )
        filters = {
                "employee": ["in", employees],
                "date_from": ["<=", self.date_from],
                "date_to": [">=", self.date_to],
                "docstatus": ["!=",2]
            }
        or_filters = {"dust_added": ["is","NULL"], "dust_added": ['not like', f'%{self.dustname}%']}
        if revert:
            filters["dust_added"] = ['like', f'%{self.dustname}%']
            or_filters = None
        emls = frappe.get_list(
            "Employee Metal Loss",
            filters,
            ["employee", "name", "gross_pure_metal_loss", "loss_recovered", "dust_added"],
            or_filters = or_filters
        )
        emp = set(employees).difference(set([emp.get("employee") for emp in emls]))
        if emp:
            msg = f"No Employee Metal Loss found for <b>{', '.join(emp)}</b>"
            print_msg(msg, update)
        gross_pure_metal_loss = sum(eml.get("gross_pure_metal_loss", 0) for eml in emls)
        for eml in emls:
            loss_recovered = (
                flt(fine_weight)
                / gross_pure_metal_loss
                * eml.get("gross_pure_metal_loss", 0)
            )
            f_loss_recovered = flt(eml.get("loss_recovered")) + loss_recovered
            if eml.get("gross_pure_metal_loss", 0) < f_loss_recovered:
                print_msg(
                    f"Calculated loss recovered({f_loss_recovered}) is greater than Total metal loss({eml.get('gross_pure_metal_loss')}).", update
                )
            dusts = (eml.get('dust_added') or '') + self.dustname + ', '
            if revert:
                dusts = eml.get('dust_added','').replace(f'{self.dustname}, ', '')
                f_loss_recovered = eml.get("loss_recovered") - loss_recovered
                
            if update or revert:
                self.add_to_child("Employee Metal Loss", eml.name, loss_recovered, update=update, revert=revert)
                gold_loss = eml.get("gross_pure_metal_loss") - f_loss_recovered
                frappe.db.set_value(
                    "Employee Metal Loss",
                    eml.name,
                    {"loss_recovered": f_loss_recovered, "gold_loss": gold_loss, "dust_added":dusts},
                )
    
    def add_to_child(self, doctype, docname, loss_recovered, update=False, revert=False):
        if not (update or revert):
            return
        row = {"refining": self.name,"loss_recovered":loss_recovered, "parent":docname}
        if update:
            det = frappe.get_doc(doctype, docname).append("refining_details", row)
            det.save()
        if revert:
            child = frappe.db.exists("Refining Details", row)
            frappe.delete_doc("Refining Details", child)

def make_material_receipt(qty):
    doc = frappe.new_doc("Stock Entry")
    item, warehouse = frappe.db.get_value("Jewellery Settings",None,["refined_metal", "refining_warehouse"])
    if not (item and warehouse):
        frappe.throw("Please set refining details in Jewellery Settings")
    doc.stock_entry_type = "Material Receipt"
    doc.append("items",{
        "item_code": item,
        "t_warehouse": warehouse,
        "qty": qty
    })
    doc.save()
    doc.submit()
    return doc.name

def print_msg(msg, throw=False):
    if throw:  frappe.throw(msg)
    else:   frappe.msgprint(msg)