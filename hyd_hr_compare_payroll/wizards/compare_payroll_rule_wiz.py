# -*- coding: utf-8 -*-
from datetime import date
from dateutil import relativedelta

from odoo import api, fields, models


class ComparePayrollRuleWizard(models.TransientModel):
    _name = 'hyd_hr_compare_payroll.compare_payroll_rule_wiz'

    date_start1 = fields.Date(
        string="Date start",
        required=True,
        default=lambda self: self.get_date()[2])

    date_end1 = fields.Date(
        string="Date End",
        required=True,
        default=lambda self: self.get_date()[3])

    date_start2 = fields.Date(
        string="Date start",
        required=True,
        default=lambda self: self.get_date()[0])

    date_end2 = fields.Date(
        string="Date End",
        required=True,
        default=lambda self: self.get_date()[1])

    select_rules = fields.Selection(
        string="Filter",
        selection=[
            ('appears', 'Appears on payslip'),
            ('all_rules', 'All rules'),
            ('select', 'Select rules')],
        default='appears',
        required=True)

    rules = fields.Many2many(
        string="Select rules",
        comodel_name="hr.salary.rule",
        relation="compar_payroll_to_salary_rule")

    @api.model
    def get_date(self):
        today = date.today()
        first_day_month = today.replace(day=1)
        last_day_month = first_day_month + relativedelta.relativedelta(
            months=+1,
            day=1,
            days=-1)
        first_day_prevmonth = first_day_month - relativedelta.relativedelta(
            months=1,
            day=1)
        last_day_prevmonth = first_day_month - relativedelta.relativedelta(
            days=1)
        return (first_day_month, last_day_month,
                first_day_prevmonth, last_day_prevmonth)

    @api.multi
    def print_report(self):
        self.ensure_one()
        datas = {}
        res = {}
        res['date_start1'] = self.date_start1
        res['date_end1'] = self.date_end1
        res['date_start2'] = self.date_start2
        res['date_end2'] = self.date_end2
        res['select_rules'] = self.select_rules
        res['rules'] = self.rules.mapped('id')
        datas['form'] = res

        report_name = 'hyd_hr_compare_payroll.compare_payroll_rule_report'
        return self.env.ref(report_name).report_action(self, data=datas)
