from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime

class EmployeeLoan(models.Model):
    _name = 'employee.loan'
    _description = 'Employee Loan'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    job_id = fields.Many2one('hr.job', 'Job Position', related="employee_id.job_id")
    allocation_date = fields.Datetime('Allocation Date', default=lambda self: fields.Datetime.now())
    employee_bank_account = fields.Char("Employee Bank Account")
    allocation_line_ids = fields.One2many('employee.loan.allocation.line', 'loan_id', string="Allocation Lines")
    loan_payment_ids = fields.One2many('employee.loan.payment.line', 'loan_id', string="Payment")
    move_ids = fields.Many2many('account.move', 'employee_loan_move_rel', 'loan_id', 'move_id', string="Moves", compute='get_move_ids')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)

    @api.multi
    @api.depends('allocation_line_ids', 'loan_payment_ids')
    def get_move_ids(self):
        for rec in self:
            move_ids_list = []
            for line in rec.allocation_line_ids:
                if line.move_id:
                    move_ids_list.append(line.move_id.id)
            for line in rec.loan_payment_ids:
                if line.move_id:
                    move_ids_list.append(line.move_id.id)
            rec.move_ids = [(6, 0, move_ids_list)]

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

class EmployeeLoanAllocationLine(models.Model):
    _name = 'employee.loan.allocation.line'

    loan_id = fields.Many2one('employee.loan', "Loan")
    total_loan_amount = fields.Float('Total Loan Amount')
    loan_from_date = fields.Date('From Date')
    loan_to_date = fields.Date('To Date')
    loan_payment_method = fields.Selection([('month', 'Monthly'),
                                            ('year', 'Yearly')], string="Payment Method")
    loam_amount = fields.Float("Installment Amount")
    loan_narration = fields.Char('Loan Narration')
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])
    journal_id = fields.Many2one('account.journal', string='Journal')
    state = fields.Selection([('draft', 'Draft'),
                              ('post', 'Post')], string="Status")
    move_id = fields.Many2one('account.move', string="Move")

    @api.model
    def create(self, vals):
        res = super(EmployeeLoanAllocationLine, self).create(vals)
        if res and res.state == 'post':
            if not res.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not res.account_credit or not res.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': res.loan_narration,
                'debit': res.total_loan_amount,
                'credit': 0.0,
                'account_id': res.account_debit.id,
            }
            credit_vals = {
                'name': res.loan_narration,
                'debit': 0.0,
                'credit': res.total_loan_amount,
                'account_id': res.account_credit.id,
            }
            vals = {
                'journal_id': res.journal_id.id,
                'date': datetime.now().date(),
                'ref': res.loan_id.employee_id and res.loan_id.employee_id.name or 'Employee Loan',
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            res.write({'move_id': move.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(EmployeeLoanAllocationLine, self).write(vals)
        if vals.get('state', False) and vals['state'] == 'post' and not self.move_id:
            if not self.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not self.account_credit or not self.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': self.loan_narration,
                'debit': self.total_loan_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': self.loan_narration,
                'debit': 0.0,
                'credit': self.total_loan_amount,
                'account_id': self.account_credit.id,
            }
            vals = {
                'journal_id': self.journal_id.id,
                'date': datetime.now().date(),
                'ref': self.loan_id.employee_id and self.loan_id.employee_id.name or 'Employee Loan',
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
                'name': self.loan_narration,
                'debit': self.total_loan_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': self.loan_narration,
                'debit': 0.0,
                'credit': self.total_loan_amount,
                'account_id': self.account_credit.id,
            }
            self.move_id.write({'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]})
            self.move_id.action_post()
        return res


class EmployeeLoanPaymentLine(models.Model):
    _name = 'employee.loan.payment.line'

    loan_id = fields.Many2one('employee.loan', "Loan")
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    total_amount = fields.Float('Loan Repayment')
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])
    journal_id = fields.Many2one('account.journal', string='Journal')
    state = fields.Selection([('draft', 'Draft'),
                              ('post', 'Post')], string="Status")
    move_id = fields.Many2one('account.move', string="Move")

    @api.model
    def create(self, vals):
        res = super(EmployeeLoanPaymentLine, self).create(vals)
        if res and res.state == 'post':
            if not res.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not res.account_credit or not res.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': 'Repayment - %s' % res.loan_id.employee_id.name or 'Repayment Loan',
                'debit': res.total_amount,
                'credit': 0.0,
                'account_id': res.account_debit.id,
            }
            credit_vals = {
                'name': 'Repayment - %s' % res.loan_id.employee_id.name or 'Repayment Loan',
                'debit': 0.0,
                'credit': res.total_amount,
                'account_id': res.account_credit.id,
            }
            vals = {
                'journal_id': res.journal_id.id,
                'date': datetime.now().date(),
                'ref': res.loan_id.employee_id and res.loan_id.employee_id.name or 'Employee Loan - Repayment',
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            res.write({'move_id': move.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(EmployeeLoanPaymentLine, self).write(vals)
        if vals.get('state', False) and vals['state'] == 'post' and not self.move_id:
            if not self.journal_id:
                raise UserError(_('Journal is not set!! Please Set Journal.'))
            if not self.account_credit or not self.account_debit:
                raise UserError(_('You need to set debit/credit account for validate.'))

            debit_vals = {
                'name': 'Repayment Loan - %s' % self.loan_id.employee_id.name or 'Repayment Loan',
                'debit': self.total_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': 'Repayment Loan - %s' % self.loan_id.employee_id.name or 'Repayment Loan',
                'debit': 0.0,
                'credit': self.total_amount,
                'account_id': self.account_credit.id,
            }
            vals = {
                'journal_id': self.journal_id.id,
                'date': datetime.now().date(),
                'ref': self.loan_id.employee_id and self.loan_id.employee_id.name or 'Employee Loan - Repayment',
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
                'name': 'Repayment - %s' % self.loan_id.employee_id.name or 'Repayment Loan',
                'debit': self.total_amount,
                'credit': 0.0,
                'account_id': self.account_debit.id,
            }
            credit_vals = {
                'name': 'Repayment - %s' % self.loan_id.employee_id.name or 'Repayment Loan',
                'debit': 0.0,
                'credit': self.total_amount,
                'account_id': self.account_credit.id,
            }
            self.move_id.write({'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]})
            self.move_id.action_post()
        return res