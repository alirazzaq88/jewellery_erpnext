cur_frm.set_query("warehouse", "warehouses", function(frm, cdt, cdn) {
  let d = locals[cdt][cdn]
    return {
        "filters": {
          'company': d.company
        }
  };
});
            