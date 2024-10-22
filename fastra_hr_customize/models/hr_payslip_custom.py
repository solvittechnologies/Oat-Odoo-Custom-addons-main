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
                          ('tax', 'Tax'),
                          ('employee_pension', 'Pension Employee'),
                          ('net_pay', 'Net Pay'),
                          ('incentive', 'Incentive'),
                          ('total', 'Total')]


class HRPayslipCustom(models.Model):
    _name = 'hr.payslip.custom'

    name = fields.Char("Payslip Name")
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
    payslip_custom_line_ids = fields.One2many('hr.payslip.custom.line', 'payslip_custom_id', string="Lines", copy=True)

    move_ids = fields.Many2many('account.move', 'hr_custom_move_rel', 'hr_custom_id', 'move_id', string="Moves", compute='get_move_ids')
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')
    payslip_custom_account_line_ids = fields.One2many('hr.payslip.custom.account.line', 'payslip_custom_id', string="Account Lines", copy=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    @api.multi
    @api.depends('payslip_custom_account_line_ids')
    def get_move_ids(self):
        for rec in self:
            move_ids_list = []
            for line in rec.payslip_custom_account_line_ids:
                if line.move_id:
                    move_ids_list.append(line.move_id.id)
            rec.move_ids = [(6, 0, move_ids_list)]

    @api.multi
    def action_validate(self):
        self.write({'state': 'validated'})

        vals = {'name': self.name,
                'location_id': self.location_id and self.location_id.id or False,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'month': self.month,
                'account_analytic_id': self.account_analytic_id and self.account_analytic_id.id or False,
                'line_ids': []}
        for line in self.payslip_custom_line_ids:
            vals['line_ids'].append((0, 0, {'beneficiary_name': line.employe_name and line.employe_name.name or False,
                                            'payment_amount': line.net_pay,
                                            }))
        self.env['salaries.excel.sheet'].sudo().create(vals)
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

        worksheet = workbook.add_worksheet('Payroll Report')

        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})

        row = 0
        worksheet.write(row, 0, 'Names', format1)
        worksheet.write(row, 1, 'Bank/Acct Number', format1)
        worksheet.write(row, 2, 'Gross Pay', format1)
        worksheet.write(row, 3, 'Surcharge', format1)
        worksheet.write(row, 4, 'Tax', format1)
        worksheet.write(row, 5, 'Pension Employee', format1)
        worksheet.write(row, 6, 'Net Pay', format1)
        worksheet.write(row, 7, 'Incentive', format1)
        worksheet.write(row, 8, 'Total', format1)
        row += 1

        gross_pay = sucharge = tax = employee_pension = net_pay = incentive = total = 0.0

        for line in self.payslip_custom_line_ids:
            worksheet.write(row, 0, line.employee_id and line.employee_id.name or '')
            worksheet.write(row, 1, line.bank_account_number or '')

            worksheet.write(row, 2, line.gross_pay or '')
            gross_pay += line.gross_pay
            worksheet.write(row, 3, line.sucharge or '')
            sucharge += line.sucharge
            worksheet.write(row, 4, line.tax or '')
            tax += line.tax
            worksheet.write(row, 5, line.employee_pension or '')
            employee_pension += line.employee_pension
            worksheet.write(row, 6, line.net_pay or '')
            net_pay += line.net_pay
            worksheet.write(row, 7, line.incentive or '')
            incentive += line.incentive
            worksheet.write(row, 8, line.total or '')
            total += line.total
            row += 1

        worksheet.write(row, 2, gross_pay, bold)
        worksheet.write(row, 3, sucharge, bold)
        worksheet.write(row, 4, tax, bold)
        worksheet.write(row, 5, employee_pension, bold)
        worksheet.write(row, 6, net_pay, bold)
        worksheet.write(row, 7, incentive, bold)
        worksheet.write(row, 8, total, bold)

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Payroll.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.payslip.custom&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }


class HRPayslipCustomLine(models.Model):
    _name = 'hr.payslip.custom.line'

    payslip_custom_id = fields.Many2one('hr.payslip.custom',string="Payslip Custom Id")
    employee_id = fields.Many2one('hr.employee', string="Names")
    bank_account_number = fields.Char("Bank/Acct Number")
    gross_pay = fields.Integer("Gross Pay")
    sucharge = fields.Integer("Surcharge")
    tax = fields.Float("Tax")
    employee_pension = fields.Float("Pension Employee")
    net_pay = fields.Float("Net Pay")
    incentive = fields.Float("Incentive")
    total = fields.Float("Total")

    @api.onchange('gross_pay')
    def onchange_gross_pay(self):
        self.tax = 0.1015467 * self.gross_pay
        self.employee_pension = 0.072 * self.gross_pay
        self.incentive = 0.2 * self.gross_pay

    @api.onchange('gross_pay', 'sucharge', 'tax', 'employee_pension')
    def onchange_net_pay(self):
        self.net_pay = self.gross_pay - self.sucharge + self.tax + self.employee_pension

    @api.onchange('incentive', 'net_pay')
    def onchange_total(self):
        self.total = self.net_pay + self.incentive


class HRPayslipCustomAccountLine(models.Model):
    _name = 'hr.payslip.custom.account.line'

    payslip_custom_id = fields.Many2one('hr.payslip.custom',string="Payslip Custom Id")
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])
    journal_id = fields.Many2one('account.journal', string='Journal')
    payroll_type = fields.Selection(selection=Payroll_Type_Selection, string="Payroll Type")
    type_amount = fields.Float('Type Amount', compute='get_type_amount')
    line_ids = fields.Many2many('hr.payslip.custom.line', compute='get_line_ids')
    state = fields.Selection([('draft', 'Draft'),
                              ('post', 'Post')], string="Status")
    move_id = fields.Many2one('account.move', string="Move")

    @api.model
    def create(self, vals):
        res = super(HRPayslipCustomAccountLine, self).create(vals)
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
                'ref': res.payslip_custom_id.name,
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            res.write({'move_id': move.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(HRPayslipCustomAccountLine, self).write(vals)
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
                'ref': self.payslip_custom_id.name,
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
    @api.depends('payslip_custom_id', 'payslip_custom_id.payslip_custom_line_ids')
    def get_line_ids(self):
        for rec in self:
            if rec.payslip_custom_id and rec.payslip_custom_id.payslip_custom_line_ids:
                rec.line_ids = [(6, 0, rec.payslip_custom_id.payslip_custom_line_ids.ids)]
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
            if rec.payroll_type == 'tax':
                rec.type_amount = sum(rec.line_ids.mapped('tax'))
            if rec.payroll_type == 'employee_pension':
                rec.type_amount = sum(rec.line_ids.mapped('employee_pension'))
            if rec.payroll_type == 'net_pay':
                rec.type_amount = sum(rec.line_ids.mapped('net_pay'))
            if rec.payroll_type == 'incentive':
                rec.type_amount = sum(rec.line_ids.mapped('incentive'))
            if rec.payroll_type == 'total':
                rec.type_amount = sum(rec.line_ids.mapped('total'))
