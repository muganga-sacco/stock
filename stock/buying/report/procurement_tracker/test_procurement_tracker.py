# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from datetime import datetime

import frappe
from frappe.tests.utils import FrappeTestCase

from stock.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from stock.buying.report.procurement_tracker.procurement_tracker import execute
from stock.stock.doctype.material_request.material_request import make_purchase_order
from stock.stock.doctype.material_request.test_material_request import make_material_request
from stock.stock.doctype.warehouse.test_warehouse import create_warehouse


class TestProcurementTracker(FrappeTestCase):
	pass
