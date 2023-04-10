frappe.ui.form.on('BOM', {
	setup: function(frm){
		frm.set_query('item', function(doc) {
				return{ filters: {'is_system_item': 0}}
		});
	},
	validate: function(frm){
		calculate_total(frm)
	}
})

frappe.ui.form.on('BOM Metal Detail', {
	cad_weight: function(frm, cdt, cdn){
		let d = locals[cdt][cdn]
		if(d.cad_weight && d.cad_to_finish_ratio){
			frappe.model.set_value(d.doctype, d.name, 'quantity',flt(d.cad_weight * d.cad_to_finish_ratio / 100))
		}
	},
	cad_to_finish_ratio: function(frm, cdt, cdn){
		let d = locals[cdt][cdn]
		if(d.cad_weight && d.cad_to_finish_ratio){
			frappe.model.set_value(d.doctype, d.name, 'quantity',flt(d.cad_weight * d.cad_to_finish_ratio / 100))
		}
	},
	
	quantity: function(frm){
		calculate_total(frm)
	}
})
frappe.ui.form.on('BOM Diamond Detail', {
	stone_shape: function(frm, cdt, cdn){
		let d = locals[cdt][cdn]
		if(d.stone_shape == "Round" && d.pcs && d.weight_per_pcs){
			frappe.model.set_value(d.doctype, d.name, 'quantity',flt(d.pcs * d.weight_per_pcs))
		}
	},
	pcs: function(frm, cdt, cdn){
		let d = locals[cdt][cdn]
		if(d.stone_shape == "Round" && d.pcs && d.weight_per_pcs){
			frappe.model.set_value(d.doctype, d.name, 'quantity',flt(d.pcs * d.weight_per_pcs))
		}
		calculate_total(frm)
	},
	weight_per_pcs: function(frm, cdt, cdn){
		let d = locals[cdt][cdn]
		if(d.stone_shape == "Round" && d.pcs && d.weight_per_pcs){
			frappe.model.set_value(d.doctype, d.name, 'quantity',flt(d.pcs * d.weight_per_pcs))
		}
	},
	quantity: function(frm){
		calculate_total(frm)
	}
})
frappe.ui.form.on('BOM Gemstone Detail', {
	quantity: function(frm){
		calculate_total(frm)
	},
	pcs: function(frm){
		calculate_total(frm)
	}
})
frappe.ui.form.on('BOM Finding Detail', {
	quantity: function(frm){
		calculate_total(frm)
	}
})
function calculate_total(frm){
	let total_metal_weight = 0
	let diamond_weight = 0
	let total_gemstone_weight = 0
	let finding_weight = 0
	let total_diamond_pcs = 0
	let total_gemstone_pcs = 0

	if(frm.doc.metal_detail){
		frm.doc.metal_detail.forEach(function(d){
			total_metal_weight += d.quantity
		})
	}
	if(frm.doc.diamond_detail){
		frm.doc.diamond_detail.forEach(function(d){
			diamond_weight += d.quantity
			total_diamond_pcs += d.pcs
		})
	}
	if(frm.doc.gemstone_detail){
		frm.doc.gemstone_detail.forEach(function(d){
			total_gemstone_weight += d.quantity
			total_gemstone_pcs += d.pcs
		})
	}
	if(frm.doc.finding_detail){
		frm.doc.finding_detail.forEach(function(d){
			if(d.finding_category != 'Chains'){
				finding_weight += d.quantity
			}
		})
	}
	frm.set_value('total_metal_weight',total_metal_weight)
	
	frm.set_value('total_diamond_pcs',total_diamond_pcs)
	frm.set_value('diamond_weight',diamond_weight)
	frm.set_value('total_diamond_weight',diamond_weight)
	
	frm.set_value('total_gemstone_pcs',total_gemstone_pcs)
	frm.set_value('gemstone_weight',total_gemstone_weight)
	frm.set_value('total_gemstone_weight',total_gemstone_weight)
	
	frm.set_value('finding_weight',finding_weight)
	frm.set_value('metal_and_finding_weight',frm.doc.total_metal_weight + frm.doc.finding_weight)
	if(frm.doc.metal_and_finding_weight){frm.set_value('gold_to_diamond_ratio',frm.doc.metal_and_finding_weight / frm.doc.diamond_weight)}
	if(frm.doc.total_diamond_pcs){frm.set_value('diamond_ratio',frm.doc.diamond_weight/ frm.doc.total_diamond_pcs)}
	
}