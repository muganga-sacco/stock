# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import datetime
from collections import OrderedDict
from typing import Dict, List, Tuple, Union

import frappe
from frappe import _
from frappe.utils import date_diff


Filters = frappe._dict
Row = frappe._dict
Data = List[Row]
Columns = List[Dict[str, str]]
DateTime = Union[datetime.date, datetime.datetime]
FilteredEntries = List[Dict[str, Union[str, float, DateTime, None]]]
ItemGroupsDict = Dict[Tuple[int, int], Dict[str, Union[str, int]]]
SVDList = List[frappe._dict]


def execute(filters: Filters) -> Tuple[Columns, Data]:
	update_filters_with_account(filters)
	validate_filters(filters)
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def update_filters_with_account(filters: Filters) -> None:
	account = frappe.get_value("Company", filters.get("company"), "default_expense_account")
	filters.update(dict(account=account))


def validate_filters(filters: Filters) -> None:
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def get_columns() -> Columns:
	return [
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Data", "width": "200"},
		{"label": _("COGS Debit"), "fieldname": "cogs_debit", "fieldtype": "Currency", "width": "200"},
	]





def get_stock_value_difference_list(filtered_entries: FilteredEntries) -> SVDList:
	voucher_nos = [fe.get("voucher_no") for fe in filtered_entries]
	svd_list = frappe.get_list(
		"Stock Ledger Entry",
		fields=["item_code", "stock_value_difference"],
		filters=[("voucher_no", "in", voucher_nos), ("is_cancelled", "=", 0)],
	)
	assign_item_groups_to_svd_list(svd_list)
	return svd_list


def get_leveled_dict() -> OrderedDict:
	item_groups_dict = get_item_groups_dict()
	lr_list = sorted(item_groups_dict, key=lambda x: int(x[0]))
	leveled_dict = OrderedDict()
	current_level = 0
	nesting_r = []
	for l, r in lr_list:
		while current_level > 0 and nesting_r[-1] < l:
			nesting_r.pop()
			current_level -= 1

		leveled_dict[(l, r)] = {
			"level": current_level,
			"name": item_groups_dict[(l, r)]["name"],
			"is_group": item_groups_dict[(l, r)]["is_group"],
		}

		if int(r) - int(l) > 1:
			current_level += 1
			nesting_r.append(r)

	update_leveled_dict(leveled_dict)
	return leveled_dict


def assign_self_values(leveled_dict: OrderedDict, svd_list: SVDList) -> None:
	key_dict = {v["name"]: k for k, v in leveled_dict.items()}
	for item in svd_list:
		key = key_dict[item.get("item_group")]
		leveled_dict[key]["self_value"] += -item.get("stock_value_difference")


def assign_agg_values(leveled_dict: OrderedDict) -> None:
	keys = list(leveled_dict.keys())[::-1]
	prev_level = leveled_dict[keys[-1]]["level"]
	accu = [0]
	for k in keys[:-1]:
		curr_level = leveled_dict[k]["level"]
		if curr_level == prev_level:
			accu[-1] += leveled_dict[k]["self_value"]
			leveled_dict[k]["agg_value"] = leveled_dict[k]["self_value"]

		elif curr_level > prev_level:
			accu.append(leveled_dict[k]["self_value"])
			leveled_dict[k]["agg_value"] = accu[-1]

		elif curr_level < prev_level:
			accu[-1] += leveled_dict[k]["self_value"]
			leveled_dict[k]["agg_value"] = accu[-1]

		prev_level = curr_level

	# root node
	rk = keys[-1]
	leveled_dict[rk]["agg_value"] = sum(accu) + leveled_dict[rk]["self_value"]


def get_row(name: str, value: float, is_bold: int, indent: int) -> Row:
	item_group = name
	if is_bold:
		item_group = frappe.bold(item_group)
	return frappe._dict(item_group=item_group, cogs_debit=value, indent=indent)


def assign_item_groups_to_svd_list(svd_list: SVDList) -> None:
	ig_map = get_item_groups_map(svd_list)
	for item in svd_list:
		item.item_group = ig_map[item.get("item_code")]


def get_item_groups_map(svd_list: SVDList) -> Dict[str, str]:
	item_codes = set(i["item_code"] for i in svd_list)
	ig_list = frappe.get_list(
		"Item", fields=["item_code", "item_group"], filters=[("item_code", "in", item_codes)]
	)
	return {i["item_code"]: i["item_group"] for i in ig_list}


def get_item_groups_dict() -> ItemGroupsDict:
	item_groups_list = frappe.get_all("Item Group", fields=("name", "is_group", "lft", "rgt"))
	return {
		(i["lft"], i["rgt"]): {"name": i["name"], "is_group": i["is_group"]} for i in item_groups_list
	}


def update_leveled_dict(leveled_dict: OrderedDict) -> None:
	for k in leveled_dict:
		leveled_dict[k].update({"self_value": 0, "agg_value": 0})
