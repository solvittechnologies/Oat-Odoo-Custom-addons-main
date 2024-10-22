# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ReportHRPayslipCustomLibeReportWizard(models.TransientModel):
    _name = 'report.fastra_payslip_print.report.wizard'

    employee_id = fields.Boolean(string="Names of Employees")
    bank_account_number = fields.Boolean(string="Function")
    gross_pay = fields.Boolean("Gross Pay")
    sucharge = fields.Boolean("Surcharge")
    tax = fields.Boolean("Tax")
    employee_pension = fields.Boolean("Pension Employee")
    net_pay = fields.Boolean("Net Pay")
    incentive = fields.Boolean("Incentive")
    total = fields.Boolean("Total")

    resid = fields.Integer("res id")

    @api.multi
    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'values':self.id
        }
        return self.env.ref('fastra_payslip_print.hr_payslip_custom_report').report_action(self,data)


class ReportHRPayslipCustomLibeReportView(models.AbstractModel):
    _name = 'report.fastra_payslip_print.hr_payslip_custom_report_view'
    
    @api.model
    def _get_report_values(self, docids, data):
        getwizardValue = self.env['report.fastra_payslip_print.report.wizard'].sudo().search([('id', '=', data['values'])])

        doc = self.env['hr.payslip.custom.line'].sudo().search([('id', '=', getwizardValue.resid)])
        # currency=self.env.ref("base.main_company").currency_id
        company = doc.payslip_custom_id.company_id
        currency = company.currency_id

        return {
            'doc_ids': data['ids'],
            'doc_model': "hr.payslip.custom.line",
            'docs': doc,
            'currency': currency,
            'company': company,
            'o': doc,
            'getwizardValue': getwizardValue
        }


class HRPayslipCustomLibeReport(models.Model):
    _inherit = "hr.payslip.custom.line"

    def launch_wizard(self):
        wizard_id = self.env['report.fastra_payslip_print.report.wizard'].create({"resid": self.id}).id
        return {
            'name': 'My Wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'report.fastra_payslip_print.report.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
 

    
    

# class HRPayslipCustomLibeReport(models.Model):
#     _inherit = "hr.payslip.custom"
    
 

#     @api.multi
#     def get_all_report(self):
#         _logger.error(self.payslip_custom_line_ids)
#         for d in self.payslip_custom_line_ids:
#             _logger.error("_logger.error(d)_logger.error(d)_logger.error(d)")
#             _logger.error(d)
#             return self.env.ref('fastra_payslip_print.hr_payslip_custom_report').report_action(d.id)