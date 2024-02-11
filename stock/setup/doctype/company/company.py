# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import frappe
import frappe.defaults
from frappe import _
from frappe.cache_manager import clear_defaults_cache
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.utils import cint, formatdate, get_timestamp, today
from frappe.utils.nestedset import NestedSet, rebuild_tree

from hrms.setup.setup_wizard.operations.taxes_setup import setup_taxes_and_charges
from hrms.utils import get_account_currency


class Company(NestedSet):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        abbr: DF.Data
        accumulated_depreciation_account: DF.Link | None
        allow_account_creation_against_child_company: DF.Check
        asset_received_but_not_billed: DF.Link | None
        auto_err_frequency: DF.Literal["Daily", "Weekly"]
        auto_exchange_rate_revaluation: DF.Check
        book_advance_payments_in_separate_party_account: DF.Check
        capital_work_in_progress_account: DF.Link | None
        chart_of_accounts: DF.Literal
        company_description: DF.TextEditor | None
        company_logo: DF.AttachImage | None
        company_name: DF.Data
        cost_center: DF.Link | None
        country: DF.Link
        create_chart_of_accounts_based_on: DF.Literal["", "Standard Template", "Existing Company"]
        credit_limit: DF.Currency
        date_of_commencement: DF.Date | None
        date_of_establishment: DF.Date | None
        date_of_incorporation: DF.Date | None
        default_advance_paid_account: DF.Link | None
        default_advance_received_account: DF.Link | None
        default_bank_account: DF.Link | None
        default_buying_terms: DF.Link | None
        default_cash_account: DF.Link | None
        default_currency: DF.Link
        default_deferred_expense_account: DF.Link | None
        default_deferred_revenue_account: DF.Link | None
        default_discount_account: DF.Link | None
        default_expense_account: DF.Link | None
        default_finance_book: DF.Link | None
        default_holiday_list: DF.Link | None
        default_in_transit_warehouse: DF.Link | None
        default_income_account: DF.Link | None
        default_inventory_account: DF.Link | None
        default_letter_head: DF.Link | None
        default_payable_account: DF.Link | None
        default_provisional_account: DF.Link | None
        default_receivable_account: DF.Link | None
        default_selling_terms: DF.Link | None
        default_warehouse_for_sales_return: DF.Link | None
        depreciation_cost_center: DF.Link | None
        depreciation_expense_account: DF.Link | None
        disposal_account: DF.Link | None
        domain: DF.Data | None
        email: DF.Data | None
        enable_perpetual_inventory: DF.Check
        enable_provisional_accounting_for_non_stock_items: DF.Check
        exception_budget_approver_role: DF.Link | None
        exchange_gain_loss_account: DF.Link | None
        existing_company: DF.Link | None
        fax: DF.Data | None
        is_group: DF.Check
        lft: DF.Int
        monthly_sales_target: DF.Currency
        old_parent: DF.Data | None
        parent_company: DF.Link | None
        payment_terms: DF.Link | None
        phone_no: DF.Data | None
        registration_details: DF.Code | None
        rgt: DF.Int
        round_off_account: DF.Link | None
        round_off_cost_center: DF.Link | None
        sales_monthly_history: DF.SmallText | None
        series_for_depreciation_entry: DF.Data | None
        stock_adjustment_account: DF.Link | None
        stock_received_but_not_billed: DF.Link | None
        submit_err_jv: DF.Check
        tax_id: DF.Data | None
        total_monthly_sales: DF.Currency
        transactions_annual_history: DF.Code | None
        unrealized_exchange_gain_loss_account: DF.Link | None
        unrealized_profit_loss_account: DF.Link | None
        website: DF.Data | None
        write_off_account: DF.Link | None
    # end: auto-generated types

    nsm_parent_field = "parent_company"

    def onload(self):
        load_address_and_contact(self, "company")

    def validate(self):
        self.update_default_account = False
        if self.is_new():
            self.update_default_account = True

        self.validate_abbr()
        self.validate_currency()
        self.check_country_change()
        self.check_parent_changed()
        self.validate_parent_company()

    def validate_abbr(self):
        if not self.abbr:
            self.abbr = "".join(c[0] for c in self.company_name.split()).upper()

        self.abbr = self.abbr.strip()

        if not self.abbr.strip():
            frappe.throw(_("Abbreviation is mandatory"))

        if frappe.db.sql(
            "select abbr from tabCompany where name!=%s and abbr=%s", (self.name, self.abbr)
        ):
            frappe.throw(_("Abbreviation already used for another company"))

    def validate_currency(self):
        if self.is_new():
            return
        self.previous_default_currency = frappe.get_cached_value(
            "Company", self.name, "default_currency"
        )
        if (
            self.default_currency
            and self.previous_default_currency
            and self.default_currency != self.previous_default_currency
            # and self.check_if_transactions_exist()
        ):
            frappe.throw(
                _(
                    "Cannot change company's default currency, because there are existing transactions. Transactions must be cancelled to change the default currency."
                )
            )

    def on_update(self):
        NestedSet.on_update(self)

        if frappe.flags.country_change:
            install_country_fixtures(self.name, self.country)

        if not frappe.db.get_value("Department", {"company": self.name}):
            self.create_default_departments()

        if self.default_currency:
            frappe.db.set_value("Currency", self.default_currency, "enabled", 1)

        if (
            hasattr(frappe.local, "enable_perpetual_inventory")
            and self.name in frappe.local.enable_perpetual_inventory
        ):
            frappe.local.enable_perpetual_inventory[self.name] = self.enable_perpetual_inventory

        if frappe.flags.parent_company_changed:
            from frappe.utils.nestedset import rebuild_tree

            rebuild_tree("Company")

        frappe.clear_cache()

    def create_default_departments(self):
        records = [
            # Department
            {
                "doctype": "Department",
                "department_name": _("All Departments"),
                "is_group": 1,
                "parent_department": "",
                "__condition": lambda: not frappe.db.exists("Department", _("All Departments")),
            },
            {
                "doctype": "Department",
                "department_name": _("Accounting"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Operations"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Human Resources"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
        ]

        # Make root department with NSM updation
        make_records(records[:1])

        frappe.local.flags.ignore_update_nsm = True
        make_records(records)
        frappe.local.flags.ignore_update_nsm = False
        rebuild_tree("Department")

    def check_country_change(self):
        frappe.flags.country_change = False

        if not self.is_new() and self.country != frappe.get_cached_value(
            "Company", self.name, "country"
        ):
            frappe.flags.country_change = True

    def validate_parent_company(self):
        if self.parent_company:
            is_group = frappe.get_value("Company", self.parent_company, "is_group")

            if not is_group:
                frappe.throw(_("Parent Company must be a group company"))

    def after_rename(self, olddn, newdn, merge=False):
        self.db_set("company_name", newdn)

        frappe.db.sql(
            """update `tabDefaultValue` set defvalue=%s
			where defkey='Company' and defvalue=%s""",
            (newdn, olddn),
        )

        clear_defaults_cache()

    def abbreviate(self):
        self.abbr = "".join(c[0].upper() for c in self.company_name.split())

    def on_trash(self):
        """
        Trash accounts and cost centers for this company if no gl entry exists
        """
        NestedSet.validate_if_child_exists(self)
        frappe.utils.nestedset.update_nsm(self)

        frappe.defaults.clear_default("company", value=self.name)

        # reset default company
        frappe.db.sql(
            """update `tabSingles` set value=''
			where doctype='Global Defaults' and field='default_company'
			and value=%s""",
            self.name,
        )

        frappe.db.sql("delete from tabEmployee where company=%s", self.name)
        frappe.db.sql("delete from tabDepartment where company=%s", self.name)
        frappe.db.sql("delete from `tabTax Withholding Account` where company=%s", self.name)
        frappe.db.sql("delete from `tabTransaction Deletion Record` where company=%s", self.name)

    def check_parent_changed(self):
        frappe.flags.parent_company_changed = False

        if not self.is_new() and self.parent_company != frappe.db.get_value(
            "Company", self.name, "parent_company"
        ):
            frappe.flags.parent_company_changed = True


def get_name_with_abbr(name, company):
    company_abbr = frappe.get_cached_value("Company", company, "abbr")
    parts = name.split(" - ")

    if parts[-1].lower() != company_abbr.lower():
        parts.append(company_abbr)

    return " - ".join(parts)


def install_country_fixtures(company, country):
    try:
        module_name = f"hrms.regional.{frappe.scrub(country)}.setup.setup"
        frappe.get_attr(module_name)(company, False)
    except ImportError:
        pass
    except Exception:
        frappe.log_error("Unable to set country fixtures")
        frappe.throw(
            _("Failed to setup defaults for country {0}. Please contact support.").format(
                frappe.bold(country)
            )
        )


@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
    if parent == None or parent == "All Companies":
        parent = ""

    return frappe.db.sql(
        """
		select
			name as value,
			is_group as expandable
		from
			`tabCompany` comp
		where
			ifnull(parent_company, "")={parent}
		""".format(
            parent=frappe.db.escape(parent)
        ),
        as_dict=1,
    )


@frappe.whitelist()
def add_node():
    from frappe.desk.treeview import make_tree_args

    args = frappe.form_dict
    args = make_tree_args(**args)

    if args.parent_company == "All Companies":
        args.parent_company = None

    frappe.get_doc(args).insert()


@frappe.whitelist()
def get_default_company_address(name, sort_key="is_primary_address", existing_address=None):
    if sort_key not in ["is_shipping_address", "is_primary_address"]:
        return None

    out = frappe.db.sql(
        """ SELECT
			addr.name, addr.%s
		FROM
			`tabAddress` addr, `tabDynamic Link` dl
		WHERE
			dl.parent = addr.name and dl.link_doctype = 'Company' and
			dl.link_name = %s and ifnull(addr.disabled, 0) = 0
		"""
        % (sort_key, "%s"),
        (name),
    )  # nosec

    if existing_address:
        if existing_address in [d[0] for d in out]:
            return existing_address

    if out:
        return max(out, key=lambda x: x[1])[0]  # find max by sort_key
    else:
        return None
