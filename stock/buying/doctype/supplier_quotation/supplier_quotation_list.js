frappe.listview_settings["Supplier Quotation"] = {
	add_fields: ["supplier", "base_grand_total", "status", "company", "currency"],
	get_indicator: function (doc) {
		if (doc.status === "Ordered") {
			return [__("Ordered"), "green", "status,=,Ordered"];
		} else if (doc.status === "Rejected") {
			return [__("Lost"), "gray", "status,=,Lost"];
		} else if (doc.status === "Expired") {
			return [__("Expired"), "gray", "status,=,Expired"];
		}
	},

	onload: function (listview) {
		listview.page.add_action_item(__("Purchase Order"), () => {
			stock.bulk_transaction_processing.create(listview, "Supplier Quotation", "Purchase Order");
		});

		listview.page.add_action_item(__("Purchase Invoice"), () => {
			stock.bulk_transaction_processing.create(listview, "Supplier Quotation", "Purchase Invoice");
		});
	},
};
