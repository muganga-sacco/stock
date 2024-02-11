# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.query_builder import Field
from frappe.query_builder.functions import CombineDatetime, Min
from frappe.utils import add_days, getdate, today

import stock
from stock.stock.utils import get_stock_value_on


def execute(filters=None):
	if not stock.is_perpetual_inventory_enabled(filters.company):
		frappe.throw(
			_("Perpetual inventory required for the company {0} to view this report.").format(
				filters.company
			)
		)

	data = get_data(filters)
	columns = get_columns(filters)

	return columns, data







def get_columns(filters):
	return [
		{
			"label": _("Stock Ledger ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Stock Ledger Entry",
			"width": "80",
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date"},
		{"label": _("Posting Time"), "fieldname": "posting_time", "fieldtype": "Time"},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": "110"},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": "110",
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": "110",
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": "110",
		},
		{
			"label": _("Expected Stock Value"),
			"fieldname": "expected_stock_value",
			"fieldtype": "Currency",
			"width": "150",
		},
		{"label": _("Stock Value"), "fieldname": "stock_value", "fieldtype": "Currency", "width": "120"},
		{
			"label": _("Difference Value"),
			"fieldname": "difference_value",
			"fieldtype": "Currency",
			"width": "150",
		},
	]
