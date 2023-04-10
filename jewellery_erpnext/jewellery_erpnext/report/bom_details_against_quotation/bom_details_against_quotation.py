import frappe
from frappe import _
import json

def execute(filters=None):
        columns, data = [], []
        data = get_filtered_data(filters)
        #common_data = common_data(filters)
        # metal = get_metal(filters)
        # diamond = get_diamond(filters)
        # gemstone = get_gemstone(filters)
        # length  = max_length(filters)
        columns = get_columns(filters)

        return columns, data

def get_columns(filters):
        return [
                {"label":_("S.No."),"fieldname":"serial_no","fieldtype":"data","width":100},
                {"label":_("Image"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Category Code"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Category"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Sub Category"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Product Shape"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Supplier Style No"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Tag No"),"options":"Tag No","fieldname":"tag_no","fieldtype":"Link","width":150},
                {"label":_("Matching ID"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Product Pcs"),"fieldname":"product_pcs","fieldtype":"data","width":100},
                {"label": _("Item Code"),"options": "Item","fieldname": "item","fieldtype": "Link","width": 150,},
                {"label":_("Article_code"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Gender"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Quotation Date"),"fieldname":"quotation_date","fieldtype":"date","width":150},
                {"label":_("Design Date"),"fieldname":"","fieldtype":"date","width":150},
                {"label":_("Launch Month"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("CFA"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Brand"),"fieldname":"","fieldtype":"data","width":100},
                {"label": _("BOM ID"),"options": "BOM","fieldname": "bom","fieldtype": "Link","width": 150,},
                {"label":_("Product Size"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Total Colour Stone Pcs"),"fieldname":"total_gemstone_pcs","fieldtype":"data","width":100},
                {"label":_("Total Colour Stone CT"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Rate per pcs"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Rate per order"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Collection Name"),"fieldname":"","fieldtype":"data","width":100},
                {"label":_("Collection Code"),"fieldname":"","fieldtype":"data","width":100},
                # BOM Metal Detail Columns
                {"label": _("Metal Type"),"fieldname": "metal_type","fieldtype": "data","width": 150,},
                {"label": _("Metal Code"),"fieldname": "metal_code","fieldtype": "data","width": 150,},
                {"label": _("Metal purity"),"fieldname": "metal_purity_","fieldtype": "data","width": 150,},
                {"label":_("Product Dimension Metal Configuration"), "fieldname":"metal_purity","fieldtype":"data","width":150},
                {"label": _("Metal Colour(WatchDialMetal)"),"fieldname": "metal_colour","fieldtype": "data","width": 150,},
                {"label":_("Metal Line Number"),"fieldname":"metal_line_no","fieldtype":"data","width":150},
                {"label":_("Gross Wt"),"fieldname":"gross_weight","fieldtype":"data","width":100},
                {"label":_("Total Gold wt.(Net Wt for SKU)"),"fieldname":"total_metal_weight","fieldtype":"data","width":150},
                {"label":_("BOM Metal Item"),"options":"Item","fieldname":"bom_metal_item","fieldtype":"Link","width":150},
                {"label":_("Net Gold Weight"),"fieldname":"total_metal_weight","fieldtype":"data","width":100},
                {"label":_("Chain Item"),"fieldname":"item_category","fieldtype":"data","width":150},
                {"label":_("Chain Weight"),"fieldname":"chain_weight","fieldtype":"data","width":150},
                {"label":_("Metal Rate"),"fieldname":"gold_bom_rate","fieldtype":"float","width":100},
                {"label":_("Metal Amount"),"fieldname":"","fieldtype":"float","width":150},
                {"label":_("Finding Name"),"fieldname":"","fieldtype":"float","width":150},
                {"label":_("Finding Net Weight"),"fieldname":"","fieldtype":"float","width":150},
                {"label":_("Group Size"),"fieldname":"","fieldtype":"float","width":150},
                # BOM Diamond Detail Column
               # {"label": _("Diamond Name"),"fieldname": "dname","fieldtype": "data","width": 150,},
                {"label":_("Diamond Cut"),"fieldname":"diamond_cut","fieldtype":"float","width":150},
                {"label":_("Diamond Pcs"),"fieldname":"diamond_pcs","fieldtype":"data","width":150},
                {"label":_("Diamond Total Qty"),"fieldname":"total_diamond_weight","fieldtype":"data","width":150},
                {"label":_("Diamond Stone Name"),"fieldname":"Diamond","fieldtype":"data","width":180},
                {"label":_("Setting Type"),"fieldname":"sub_setting","fieldtype":"data","width":180},
                {"label":_("Diamond Size Name"),"fieldname":"diamond_size_name","fieldtype":"data","width":180},
                {"label":_("Diamond Stone Item"),"options":"Item","fieldname":"diamond_stone_item","fieldtype":"Link","width":150},
                {"label": _("Diamond Sieve size"),"fieldname": "diamond_sieve_size","fieldtype": "data","width": 150,},
                {"label":_("Diamond Shape"),"fieldname":"stone_shape","fieldtype":"data","width":150,},
                {"label":_("Clarity"),"fieldname":"","fieldtype":"data","width":100,},
                {"label":_("Colour"),"fieldname":"","fieldtype":"data","width":100,},
                {"label": _("Diamond Code"),"fieldname": "","fieldtype": "data","width": 150,},
                {"label":_("Diamond Shape"),"fieldname":"stone_shape","fieldtype":"data","width":150,},
                {"label": _("Diamond Stone Pcs"),"fieldname": "pcs","fieldtype": "data","width": 150,},
                {"label":_("Diamond Cts"),"fieldname":"quantity","fieldtype":"data","width":100},
                {"label": _("Dia/Pcs"),"fieldname": "weight_per_pcs","fieldtype": "data","width": 150,},
                {"label":_("Diamond Rate"),"fieldtype":"", "fieldtype":"data","width":150},
                {"label":_("Diamond Amount"),"fieldtype":"", "fieldtype":"data","width":150},
                {"label":_("Total Diamond Amount"),"fieldtype":"", "fieldtype":"data","width":150},
                {"label":_("Diamond Stone Ct Unit"),"fieldtype":"CT", "fieldtype":"data","width":150},
                # BOM Gemstone Detail Column
               # {"label": _("GEM Name"),"fieldname": "gname","fieldtype": "data","width": 150,},
                {"label": _("Colour Stone Item"),"fieldname": "gemstone_type","fieldtype": "data","width": 150,},
                {"label":_("Colour Stone Shape"),"fieldname":"color_stone_shape","fieldtype":"data","width":180},
                {"label": _("Colored Stone Cut/Vendor"),"fieldname": "cut_or_cab","fieldtype": "data","width": 150,},
                {"label":_("Colour Stone Size"),"fieldname":"gemstone_size","fieldtype":"data","width":150},
                {"label":_("Colour Stone Code"),"fieldname":"gemstone_code","fieldtype":"data","width":150},
                {"label":_("Colour Stone Pcs"),"fieldname":"colour_stone_pcs","fieldtype":"data","width":150},
                {"label":_("Colour Stone Ct"),"fieldname":"colour_stone_qty","fieldtype":"data", "width":150},
                {"label":_("Colour Stone Ct Unit"),"fieldname":"CT", "fieldtype":"data","width":150},
                {"label":_("Stone Rate"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Total Stone Amount"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Category Manager"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Theme Code"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Individual Wgt"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Total Wgt"),"fieldname":"","fieldtype":"data","width":150},
                {"label":_("Customer Design Code"),"fieldname":"","fieldtype":"float","width":150},
                {"label":_("Designer"),"fieldname":"","fieldtype":"float","width":150},
                {"label":_("Product Dimension Size"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Product Dimension Group"),"fieldname":"prod_dimension_gp", "fieldtype":"data","width":150},
                {"label":_("Revision Collection"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Revision Collection Code"),"fieldname":"revision_collection_code", "fieldtype":"data","width":180},
                {"label":_("Sub Article"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Sub Article Code"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Manufacturing Type(MFG-Code)"),"fieldname":"CA", "fieldtype":"data","width":150},
                {"label":_("Style-(Pearl Type Code(WatchDialIndex)"),"fieldname":"SR", "fieldtype":"data","width":150},
                {"label":_("Set Ref-Pearl Colour(WatchDialColor)"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Set Ref-Pearl Colour Code(WatchDialColor)"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Vendor Code/Name"),"fieldname":"vendor_code", "fieldtype":"data","width":200},
                {"label":_("Manufacturing type(Mfg_description)"),"fieldname":"", "fieldtype":"data","width":150},
                {"label":_("Form/Shape"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Style"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Primary Theme"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Manufacturing Style"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Usage"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Occasion"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Finding Making Charge"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Wastage Charge"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Unit Value"),"fieldname":"", "fieldtype":"data","width":100},
                {"label":_("Final Value"),"fieldname":"", "fieldtype":"data","width":150},

                

        ]

# def common_data(filters):
#         data = get_filtered_data(filters)
#         flt_data = ""
#         dname = ""
#         mname = ""
#         gname = ""
#         bom = ""
#         lst_data = []
#         for row in data:
#                 #if same bom no. exist then below mentioned columns will get updated to null
#                 if row['bom'] in flt_data:
#                         row["bom"] = ""
#                         row["item"] = ""
#                         row["product_pcs"] = ""
#                         row["tag_no"] = ""
#                         row["item_category"] = ""
#                         row["chain_weight"]=""
#                         row["gold_bom_rate"]=""
#                         row["total_diamond_pcs"]=""
#                         row["total_diamond_weight"] = ""
#                         row["CA"]=""
#                         row["SR"]=""
#                 else:
#                         flt_data = row['bom']
#                 # if same bom_metal_id exist then below mentioned columns will get updated to null
#                 if row['mname'] in mname:
#                         row["metal_purity"] = ""
#                         row["metal_colour"] = ""
#                         row["metal_line_no"] = ""
#                         row["gross_weight"] = ""
#                         row["total_metal_weight"] =""
#                         row["bom_metal_item"]=""
#                 else:
#                         mname = row['mname']
#                 # #if same bom_diamond_detail_id exist then below mentioned columns will get updated to null
#                 if row['dname']  in dname:
#                         row["Diamond"] = ""
#                         row["diamond_stone_item"] = ""
#                         row["diamond_sieve_size"] = ""
#                         row["stone_shape"] = ""
#                         row["diamond_cut"] = ""
#                         row["pcs"]=""
#                         row["quantity"]=""
#                         row["CT"] = ""
#                         row["weight_per_pcs"] =""
#                 else:
#                         dname = row['dname']
#                 # #if same bom_gemstone_id exist then below mentioned columns will get updated to null
#                 if row['gname'] in gname:
#                         row["gemstone_type"] = ""
#                         row["cut_and_cab"]=""
#                         row["gemstone_size"]=""
#                         row["gemstone_code"]=""
#                         row["colour_stone_pcs"]=""
#                         row["colour_stone_qty"]=""
#                         row["CT"]=""
#                         row["vendor_code"] = ""
#                 else:
#                         gname = row["gname"]
#                 lst_data.append(row)

       
#         return  lst_data
        
def get_filtered_data(filters):
        metal_data = get_metal(filters)
        diamond_data = get_diamond(filters)
        gemstone_data = get_gemstone(filters)
        length = max_length(filters)
        items_data = get_items(filters)
        dname = ""
        mname = ""
        gname = ""
        bom = ""
        max_l = 0
        for l in length:
                if (l.mname >= l.dname and l.mname >= l.gname):
                                max_l = l.mname
                if (l.dname >= l.mname and l.dname >= l.gname):
                                max_l = l.dname
                if (l.gname >= l.dname and l.gname >= l.mname):
                                max_l = l.gname


        row_length = 0;
        item_list = []
        serial_no = 0;
        for item in items_data:
                        serial_no = serial_no +1
                        itemMap = {}
                        itemMap['item'] = item['item']
                        itemMap['quotation_date'] = item['quotation_date']
                        itemMap['bom'] = item['bom']
                        itemMap['serial_no'] = serial_no
                        itemMap['total_gemstone_pcs'] = item['total_gemstone_pcs']
                        metal_datalist = []
                        for metal in metal_data:
                                if (item['item'] == metal['item'] and item.bom == metal['bom']):
                                                row = {}
                                                row["bom"] = item['bom']
                                                row["item"] = item['item']
                                                row["product_pcs"] = metal['product_pcs']
                                                row["tag_no"] = metal['tag_no']
                                                row["item_category"] = metal['item_category']
                                                row["chain_weight"]= metal['chain_weight']
                                                row["gold_bom_rate"]= metal['gold_bom_rate']
                                                row["mname"] = metal['mname'] 
                                                row["metal_type"] = metal['metal_type'] 
                                                row["metal_code"] = metal['metal_code']
                                                row["metal_purity_"] = metal['metal_purity_']
                                                row["metal_colour"] = metal['metal_colour']
                                                row["metal_line_no"] = metal['metal_line_no']
                                                row["gross_weight"] = metal['gross_weight']
                                                row["total_metal_weight"] =metal['total_metal_weight']
                                                row["bom_metal_item"]=metal['bom_metal_item']
                                                metal_datalist.append(row)
                                                        
                        gemstone_datalist = []
                        for gemstone in gemstone_data:					
                                if (item['item'] == gemstone['item'] and item.bom == gemstone['bom']):
                                                row1 = {}
                                                row1["gname"] = gemstone['gname']
                                                row1["color_stone_shape"] = gemstone['color_stone_shape']
                                                row1["gemstone_type"] = gemstone['gemstone_type']
                                                row1["cut_and_cab"]=gemstone['cut_and_cab']
                                                row1["gemstone_size"]= gemstone['gemstone_size']
                                                row1["gemstone_code"]= gemstone['gemstone_code']
                                                row1["colour_stone_pcs"]= gemstone['colour_stone_pcs']
                                                row1["colour_stone_qty"]= gemstone['colour_stone_qty']
                                                row1["CT"]= ""
                                                row1["vendor_code"] = gemstone['vendor_code']
                                                gemstone_datalist.append(row1)
                        diamond_datalist = []
                        for diamond in diamond_data:
                                if (item['item'] == diamond['item'] and item['bom'] == diamond['bom']):
                                        row2 = {}
                                        row2["Diamond"] = diamond['Diamond']
                                        row2["dname"] = diamond['dname']
                                        row2["diamond_cut"] = diamond['diamond_cut']
                                        row2["diamond_pcs"] = diamond['diamond_pcs']
                                        row2["sub_setting"] = diamond['sub_setting']
                                        row2["diamond_size_name"] = diamond['diamond_size_name']
                                        row2["diamond_stone_item"] =  diamond['diamond_stone_item']
                                        row2["diamond_sieve_size"] = diamond['diamond_sieve_size']
                                        row2["stone_shape"] =diamond['stone_shape']
                                        row2["diamond_cut"] = diamond['diamond_cut']
                                        row2["pcs"]=diamond['pcs']
                                        row2["quantity"]=diamond['quantity']
                                        row2["weight_per_pcs"] =diamond['weight_per_pcs']
                                        diamond_datalist.append(row2)
                                                                        
                        itemMap['metalData'] = metal_datalist
                        itemMap['gemstoneData'] = gemstone_datalist
                        itemMap['diamondData'] = diamond_datalist
                        item_list.append(itemMap)



        lst = []
        for item in item_list:
                metal_data1 = item['metalData']
                gemstone_data1 = item['gemstoneData']
                diamond_data1 = item['diamondData']
                for i in range(0,max_l):
                        row = {}
                        if (i < len(metal_data1)):
                                        row["bom"] = item['bom']
                                        row["item"] = item['item']
                                        row['quotation_date'] = item['quotation_date']
                                        row['total_gemstone_pcs'] = item['total_gemstone_pcs']
                                        row['serial_no'] = item['serial_no']
                                        row["product_pcs"] = metal_data1[i]['product_pcs']
                                        row["tag_no"] = metal_data1[i]['tag_no']
                                        row["item_category"] = metal_data1[i]['item_category']
                                        row["chain_weight"]= metal_data1[i]['chain_weight']
                                        row["gold_bom_rate"]= metal_data1[i]['gold_bom_rate']
                                        row["mname"] = metal_data1[i]['mname']
                                        row["metal_type"] = metal_data1[i]['metal_type']
                                        row["metal_code"] = metal_data1[i]['metal_code']
                                        row["metal_purity_"] = metal_data1[i]['metal_purity_']
                                        row["metal_colour"] = metal_data1[i]['metal_colour']
                                        row["metal_line_no"] = metal_data1[i]['metal_line_no']
                                        row["gross_weight"] = metal_data1[i]['gross_weight']
                                        row["total_metal_weight"] =metal_data1[i]['total_metal_weight']
                                        row["bom_metal_item"]=metal_data1[i]['bom_metal_item']
                        if (i < len(gemstone_data1)):
                                        row["gname"] = gemstone_data1[i]['gname'] 
                                        row["color_stone_shape"] = gemstone_data1[i]['color_stone_shape']
                                        row["gemstone_type"] = gemstone_data1[i]['gemstone_type']
                                        row["cut_and_cab"]=gemstone_data1[i]['cut_and_cab']
                                        row["gemstone_size"]= gemstone_data1[i]['gemstone_size']
                                        row["gemstone_code"]= gemstone_data1[i]['gemstone_code']
                                        row["colour_stone_pcs"]= gemstone_data1[i]['colour_stone_pcs']
                                        row["colour_stone_qty"]= gemstone_data1[i]['colour_stone_qty']
                                        row["CT"]= ""
                                        row["vendor_code"] = gemstone_data1[i]['vendor_code']
                        if (i < len(diamond_data1) ):
                                        row["Diamond"] = diamond_data1[i]['Diamond']
                                        row["dname"] = diamond_data1[i]['dname']
                                        row["diamond_cut"] = diamond_data1[i]['diamond_cut']
                                        row["diamond_pcs"] = diamond_data1[i]['diamond_pcs']
                                        row["sub_setting"] = diamond_data1[i]['sub_setting']
                                        row["diamond_size_name"] = diamond_data1[i]['diamond_size_name']
                                        row["diamond_stone_item"] =  diamond_data1[i]['diamond_stone_item']
                                        row["diamond_sieve_size"] = diamond_data1[i]['diamond_sieve_size']
                                        row["stone_shape"] =diamond_data1[i]['stone_shape']
                                        row["diamond_cut"] = diamond_data1[i]['diamond_cut']
                                        row["pcs"]=diamond_data1[i]['pcs']
                                        row["quantity"]=diamond_data1[i]['quantity']
                                        row["weight_per_pcs"] =diamond_data1[i]['weight_per_pcs']
                        if row:
                                        lst.append(row)

                                        
                                        
        lst_d =[item for item in lst if item]
        return lst_d
        
        

def condition(filters):
        cond = ''
        if filters.get("qname"):
                cond = cond + f"""where  q.name = "{filters.get('qname')}" """
        return cond


# def get_data(filters):
#         conditions=condition(filters)
#         data  = frappe.db.sql(f"""select qi.gold_bom_rate,b.tag_no,qi.qty as 'product_pcs',qi.item_code as "item",ifnull(qi.quotation_bom,"NA") as 'bom',
#                                 ifnull(bmd.name,"NA") as "mname",CONCAT(bmd.metal_type,'_ ',bmd.purity_percentage) as metal_purity_ ,bmd.purity_percentage,bmd.metal_purity,bmd.metal_colour,cmn.metal_line_no,b.gross_weight,
#                                 b.total_metal_weight,bmd.item as bom_metal_item,b.item_category,b.chain_weight,qi.gold_bom_rate,
#                                 b.total_diamond_pcs,b.total_diamond_weight,"Diamond",bdm.item as "diamond_stone_item",
#                                 ifnull(bdm.name,"NA") as "dname",bdm.diamond_sieve_size,bdm.stone_shape,bdm.diamond_cut,bdm.pcs,bdm.quantity,bdm.weight_per_pcs,"CT",
#                                 ifnull(bgd.name,"NA") as "gname",bgd.gemstone_type,bgd.cut_and_cab ,bgd.gemstone_size,bgd.gemstone_code, bgd.pcs as colour_stone_pcs,bgd.quantity as "colour_stone_qty","CT",

#                                 CONCAT(cpd.code,"",cpd.product_dimension) as "prod_dimension_gp", CONCAT(ccc.code,"",ccc.collection) as "revision_collection_code","CA" ,"SR",c.vendor_code

#                                 from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
#                                 left join `tabCustomer` c on c.name =  q.party_name  left join `tabCustomer Metal Line No` cmn on cmn.parent = c.name
#                                 left join  `tabCustomer Product Dimension Code` cpd  on cpd.parent = c.name left join `tabCustomer Collection Code` ccc on ccc.parent = c.name
#                                 left join `tabBOM`b on b.name = qi.quotation_bom right join `tabBOM Metal Detail` bmd  on bmd.parent = b.name right join `tabBOM Diamond Detail` bdm on bdm.parent = b.name
#                                 right join `tabBOM Gemstone Detail` bgd  on bgd.parent = b.name
                               
#                                 where  %s """ % conditions, filters ,as_dict= True)

        
        
#         return data


def get_metal(filters):
        conditions=condition(filters)
        metal_data  = frappe.db.sql(f"""select qi.gold_bom_rate,b.tag_no,qi.qty as 'product_pcs',qi.item_code as "item",ifnull(qi.quotation_bom,"NA") as 'bom',
                                ifnull(bmd.name,"NA") as "mname",bmd.metal_type as metal_type,bmd.metal_purity as metal_code,CONCAT(bmd.metal_type,'_ ',bmd.purity_percentage) as metal_purity_ ,bmd.purity_percentage,bmd.metal_purity,bmd.metal_colour,cmn.metal_line_no,b.gross_weight,
                                b.total_metal_weight,bmd.item as bom_metal_item,b.item_category,b.chain_weight,qi.gold_bom_rate
				from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
                                left join `tabCustomer` c on c.name =  q.party_name  left join `tabCustomer Metal Line No` cmn on cmn.parent = c.name
                                left join  `tabCustomer Product Dimension Code` cpd  on cpd.parent = c.name left join `tabCustomer Collection Code` ccc on ccc.parent = c.name
                                left join `tabBOM`b on b.name = qi.quotation_bom left join `tabBOM Metal Detail` bmd  on bmd.parent = b.name
                               %s """ % conditions, filters ,as_dict= True)
        return metal_data
def get_diamond(filters):
        conditions=condition(filters)
        diamond_data  = frappe.db.sql(f"""select qi.item_code as "item",ifnull(qi.quotation_bom,"NA") as 'bom',bdm.pcs as 'diamond_pcs',b.total_diamond_weight,"Diamond",bdm.item as "diamond_stone_item",
                                ifnull(bdm.name,"NA") as "dname",bdm.diamond_cut as "diamond_cut",bdm.setting_type as "sub_setting",bdm.size_type as "diamond_size_name", bdm.diamond_sieve_size,bdm.stone_shape,bdm.diamond_cut,bdm.pcs,bdm.quantity,bdm.weight_per_pcs,"CT"
                                from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
                                left join `tabCustomer` c on c.name =  q.party_name  left join `tabCustomer Metal Line No` cmn on cmn.parent = c.name
                                left join  `tabCustomer Product Dimension Code` cpd  on cpd.parent = c.name left join `tabCustomer Collection Code` ccc on ccc.parent = c.name
                                left join `tabBOM`b on b.name = qi.quotation_bom left join `tabBOM Diamond Detail` bdm on bdm.parent = b.name
                                %s """ % conditions, filters ,as_dict= True)
        return diamond_data

def get_gemstone(filters):
        conditions=condition(filters)
        gemstone_data  = frappe.db.sql(f"""select qi.item_code as "item",ifnull(qi.quotation_bom,"NA") as 'bom', ifnull(bgd.name,"NA") as "gname",bgd.stone_shape as "color_stone_shape",bgd.gemstone_type,bgd.cut_and_cab ,bgd.gemstone_size,bgd.gemstone_code, bgd.pcs as colour_stone_pcs,bgd.quantity as "colour_stone_qty","CT",
                                CONCAT(cpd.code,"",cpd.product_dimension) as "prod_dimension_gp", CONCAT(ccc.code,"",ccc.collection) as "revision_collection_code","CA" ,"SR",c.vendor_code
                                from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
                                left join `tabCustomer` c on c.name =  q.party_name  left join `tabCustomer Metal Line No` cmn on cmn.parent = c.name
                                left join  `tabCustomer Product Dimension Code` cpd  on cpd.parent = c.name left join `tabCustomer Collection Code` ccc on ccc.parent = c.name
                                left join `tabBOM`b on b.name = qi.quotation_bom left join `tabBOM Gemstone Detail` bgd  on bgd.parent = b.name
                                %s """ % conditions, filters ,as_dict= True)
        return gemstone_data


def max_length(filters):
        conditions= condition(filters)
        length = frappe.db.sql(f""" select q.name,count(distinct bmd.name) as "mname",count(distinct bgd.name) as "gname",count(distinct bdm.name) as "dname"from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
                                left join `tabCustomer` c on c.name =  q.party_name  left join `tabCustomer Metal Line No` cmn on cmn.parent = c.name
                                left join  `tabCustomer Product Dimension Code` cpd  on cpd.parent = c.name left join `tabCustomer Collection Code` ccc on ccc.parent = c.name
                                left join `tabBOM`b on b.name = qi.quotation_bom right join `tabBOM Metal Detail` bmd  on bmd.parent = b.name
                                left join `tabBOM Diamond Detail` bdm on bdm.parent = b.name
                                left join `tabBOM Gemstone Detail` bgd  on bgd.parent = b.name
                                %s """ %conditions, filters ,as_dict= True)
        return length

def get_items(filters):
        conditions= condition(filters)
        items_data = frappe.db.sql(f""" select q.name,q.transaction_date as 'quotation_date', qi.item_code as "item", ifnull(qi.quotation_bom,"NA") as 'bom',b.total_gemstone_pcs as "total_gemstone_pcs" from `tabQuotation` q left join `tabQuotation Item` qi on qi.parent = q.name
                                 left join `tabBOM` b on b.name = qi.quotation_bom
                                %s """ %conditions, filters ,as_dict= True)
        # frappe.msgprint(length)
        return items_data

