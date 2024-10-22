from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64
from io import BytesIO

Months = [('January', 'January'),
          ('february', 'February'),
          ('march', 'March'),
          ('april', 'April'),
          ('may', 'May'),
          ('june', 'June'),
          ('july', 'July'),
          ('august', 'August'),
          ('september', 'September'),
          ('october', 'October'),
          ('november', 'November'),
          ('december', 'December')]

Payroll_Type_Selection = [('gross_pay', 'Gross Pay'),
                          ('sucharge', 'Surcharge'),
                          ('wht', 'WHT'),
                          ('net_pay', 'Net Pay')]


class SupervisoryFee(models.Model):
    _name = 'supervisory.fee'

    name = fields.Char("Name")
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated')], string="State", default='draft')
    location_id = fields.Many2one('stock.location', "Location")
    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            )
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                          )
    month = fields.Selection(Months, string="Month")
    employee_tag = fields.Char("Reference Number")
    account_analytic_id = fields.Many2one('account.analytic.account', "Analytic Account")
    line_ids = fields.One2many('supervisory.fee.line', 'supervisory_fee_id', string="Lines", copy=True)

    move_ids = fields.Many2many('account.move', 'supervisory_fee_move_rel', 'supervisory_fee_id', 'move_id', string="Moves", compute='get_move_ids')
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')
    account_line_ids = fields.One2many('supervisory.fee.account.line', 'supervisory_fee_id', string="Account Lines", copy=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    @api.multi
    @api.depends('account_line_ids')
    def get_move_ids(self):
        for rec in self:
            move_ids_list = []
            for line in rec.account_line_ids:
                if line.move_id:
                    move_ids_list.append(line.move_id.id)
            rec.move_ids = [(6, 0, move_ids_list)]

    @api.multi
    def action_validate(self):
        self.write({'state': 'validated'})
        return

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.move_ids.ids)],
        }

    def generate_excel(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Supervisory Fee Report')

        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})

        row = 0
        worksheet.write(row, 0, 'Names', format1)
        worksheet.write(row, 1, 'Bank/Acct Number', format1)
        worksheet.write(row, 2, 'Gross Pay', format1)
        worksheet.write(row, 3, 'WHT (5%)', format1)
        worksheet.write(row, 4, 'Surcharge', format1)
        worksheet.write(row, 5, 'Net Pay', format1)
        row += 1

        gross_pay = sucharge = wht = net_pay = 0.0

        for line in self.line_ids:
            worksheet.write(row, 0, line.employee_id and line.employee_id.name or '')
            worksheet.write(row, 1, line.bank_account_number or '')

            worksheet.write(row, 2, line.gross_pay or '')
            gross_pay += line.gross_pay
            worksheet.write(row, 3, line.wht or '')
            wht += line.wht
            worksheet.write(row, 4, line.sucharge or '')
            sucharge += line.sucharge
            worksheet.write(row, 5, line.net_pay or '')
            net_pay += line.net_pay
            row += 1

        worksheet.write(row, 2, gross_pay, bold)
        worksheet.write(row, 3, wht, bold)
        worksheet.write(row, 4, sucharge, bold)
        worksheet.write(row, 5, net_pay, bold)

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Supervisory Fee.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=supervisory.fee&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }


class SupervisoryFeeLine(models.Model):
    _name = 'supervisory.fee.line'

    supervisory_fee_id = fields.Many2one('supervisory.fee', string="Supervisory Fee")
    employee_id = fields.Many2one('hr.employee', string="Names")
    bank_account_number = fields.Char("Bank/Acct Number")
    gross_pay = fields.Integer("Gross Pay")
    wht = fields.Integer("WHT (5%)")
    sucharge = fields.Integer("Surcharge")
    net_pay = fields.Float("Net Pay")
    comment = fields.Char("Remark")

    @api.onchange('gross_pay', 'sucharge', 'wht')
    def onchange_net_pay(self):
        self.net_pay = self.gross_pay - self.sucharge - self.wht

    def launch_wizard(self):
        wizard_id = self.env['report.fastra_hr_customize.report.wizard'].create({"resid": self.id}).id
        return {
            'name': 'Supervisory Fee Report Wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'report.fastra_hr_customize.report.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class SupervisoryFeeAccountLine(models.Model):
    _name = 'supervisory.fee.account.line'

    supervisory_fee_id = fields.Many2one('supervisory.fee', string="Supervisory Fee")
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])
    journal_id = fields.Many2one('account.journal', string='Journal')
    payroll_type = fields.Selection(selection=Payroll_Type_Selection, string="Payroll Type")
    type_amount = fields.Float('Type Amount', compute='get_type_amount')
    line_ids = fields.Many2many('supervisory.fee.line', compute='get_line_ids')
    state = fields.Selection([('draft', 'Draft'),
                              ('post', 'Post')], string="Status")
    move_id = fields.Many2one('account.move', string="Move")

    @api.model
    def create(self, vals):
        res = super(SupervisoryFeeAccountLine, self).create(vals)
        if res and res.state == 'post':
            if not res.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not res.account_credit or not res.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': dict(res._fields['payroll_type'].selection).get(res.payroll_type),
                'debit': res.type_amount,
                'credit': 0.0,
                'account_id': res.account_debit.id,
            }
            credit_vals = {
                'name': dict(res._fields['payroll_type'].selection).get(res.payroll_type),
                'debit': 0.0,
                'credit': res.type_amount,
                'account_id': res.account_credit.id,
            }
            vals = {
                'journal_id': res.journal_id.id,
                'date': datetime.now().date(),
                'ref': res.supervisory_fee_id.name,
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            res.write({'move_id': move.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(SupervisoryFeeAccountLine, self).write(vals)
        if vals.get('state', False) and vals['state'] == 'post' and not self.move_id:
            if not self.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not self.account_credit or not self.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': dict(self._fields['payroll_type'].selection).get(self.payroll_type),
                'debit': self.type_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': dict(self._fields['payroll_type'].selection).get(self.payroll_type),
                'debit': 0.0,
                'credit': self.type_amount,
                'account_id': self.account_credit.id,
            }
            vals = {
                'journal_id': self.journal_id.id,
                'date': datetime.now().date(),
                'ref': self.supervisory_fee_id.name,
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            self.write({'move_id': move.id})
        if vals.get('state', False) and vals['state'] == 'post' and self.move_id:
            self.move_id.button_cancel()
            self.move_id.line_ids.unlink()
            debit_vals = {
                'name': dict(self._fields['payroll_type'].selection).get(self.payroll_type),
                'debit': self.type_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': dict(self._fields['payroll_type'].selection).get(self.payroll_type),
                'debit': 0.0,
                'credit': self.type_amount,
                'account_id': self.account_credit.id,
            }
            self.move_id.write({'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]})
            self.move_id.action_post()
        return res

    @api.multi
    @api.depends('supervisory_fee_id', 'supervisory_fee_id.line_ids')
    def get_line_ids(self):
        for rec in self:
            if rec.supervisory_fee_id and rec.supervisory_fee_id.line_ids:
                rec.line_ids = [(6, 0, rec.supervisory_fee_id.line_ids.ids)]
            else:
                rec.line_ids = [(6, 0, [])]

    @api.multi
    @api.depends('payroll_type', 'line_ids')
    def get_type_amount(self):
        for rec in self:
            rec.type_amount = 0.0
            if rec.payroll_type == 'gross_pay':
                rec.type_amount = sum(rec.line_ids.mapped('gross_pay'))
            if rec.payroll_type == 'sucharge':
                rec.type_amount = sum(rec.line_ids.mapped('sucharge'))
            if rec.payroll_type == 'wht':
                rec.type_amount = sum(rec.line_ids.mapped('wht'))
            if rec.payroll_type == 'net_pay':
                rec.type_amount = sum(rec.line_ids.mapped('net_pay'))


class ReportSupervisoryFeeReportWizard(models.TransientModel):
    _name = 'report.fastra_hr_customize.report.wizard'

    employee_id = fields.Boolean(string="Names of Employees")
    bank_account_number = fields.Boolean(string="Function")
    gross_pay = fields.Boolean("Gross Pay")
    sucharge = fields.Boolean("Surcharge")
    wht = fields.Boolean("WHT")
    net_pay = fields.Boolean("Net Pay")
    resid = fields.Integer("res id")

    @api.multi
    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'values': self.id
        }
        return self.env.ref('fastra_hr_customize.supervisory_fee_report').report_action(self, data)


class ReportSupervisoryFeeReportView(models.AbstractModel):
    _name = 'report.fastra_hr_customize.supervisory_fee_report_view'

    @api.model
    def _get_report_values(self, docids, data):
        getwizardValue = self.env['report.fastra_hr_customize.report.wizard'].sudo().search([('id', '=', data['values'])])

        doc = self.env['supervisory.fee.line'].sudo().search([('id', '=', getwizardValue.resid)])
        company = doc.supervisory_fee_id.company_id
        currency = company.currency_id

        return {
            'doc_ids': data['ids'],
            'doc_model': "supervisory.fee.line",
            'docs': doc,
            'currency': currency,
            'company': company,
            'o': doc,
            'getwizardValue': getwizardValue
        }