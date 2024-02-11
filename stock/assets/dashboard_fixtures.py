# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import json

import frappe
from frappe import _
from frappe.utils import get_date_str, nowdate

from stock.buying.dashboard_fixtures import get_company_for_dashboards





def get_dashboards():
	return [
		{
			"name": "Asset",
			"dashboard_name": "Asset",
			"charts": [
				{"chart": "Asset Value Analytics", "width": "Full"},
				{"chart": "Category-wise Asset Value", "width": "Half"},
				{"chart": "Location-wise Asset Value", "width": "Half"},
			],
			"cards": [
				{"card": "Total Assets"},
				{"card": "New Assets (This Year)"},
				{"card": "Asset Value"},
			],
		}
	]




def get_number_cards( year_start_date, year_end_date):
	return [
		{
			"name": "Total Assets",
			"label": _("Total Assets"),
			"function": "Count",
			"document_type": "Asset",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": "[]",
			"doctype": "Number Card",
		},
		{
			"name": "New Assets (This Year)",
			"label": _("New Assets (This Year)"),
			"function": "Count",
			"document_type": "Asset",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps(
				[["Asset", "creation", "between", [year_start_date, year_end_date]]]
			),
			"doctype": "Number Card",
		},
		{
			"name": "Asset Value",
			"label": _("Asset Value"),
			"function": "Sum",
			"aggregate_function_based_on": "value_after_depreciation",
			"document_type": "Asset",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": "[]",
			"doctype": "Number Card",
		},
	]
