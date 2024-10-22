from odoo import fields, models, api


class HrLeaveRequest(models.Model):
    _name = 'fastra.leave.request'
    _rec_name = 'hr_employee_id'
    _inherit = ['mail.thread']

    staff_number = fields.Char("Staff Number")
    state = fields.Selection([('draft', 'Draft'),
                              ('send_to_admin', 'Send to Admin'),
                              ('send_to_md', 'Send to MD'),
                              ('approve', 'Approve'),
                              ('reject', 'Reject')], string="Status", default='draft', track_visibility='always')
    hr_employee_id = fields.Many2one('hr.employee', string="Name")
    department = fields.Many2one('hr.department', string="Department")
    date = fields.Date("Date")
    leave_line_ids = fields.One2many('fastra.leave.lines', 'leave_request_id', string="Leave Lines")
    arrears = fields.Integer("Arrears")
    current = fields.Integer("Current")
    total = fields.Integer("Total", compute='get_total')
    no_of_days_taken = fields.Integer("No of Days Already taken")
    leave_balance = fields.Integer("Leave Balance")
    leave_allowance = fields.Integer("Leave Allowance")
    leave_allowance_due = fields.Integer("Leave Allowance Due")
    date_of_payment = fields.Date("Date of payment")
    reject_reason = fields.Char("Reject reason")

    @api.multi
    @api.depends('arrears', 'current')
    def get_total(self):
        for rec in self:
            rec.total = rec.arrears - rec.current

    @api.multi
    def send_to_admin(self):
        self.write({'state': 'send_to_admin'})

    @api.multi
    def send_to_md(self):
        self.write({'state': 'send_to_md'})

    @api.multi
    def approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def reject(self):
        self.write({'state': 'reject'})


class FastraLeaveLines(models.Model):
    _name = 'fastra.leave.lines'

    leave_request_id = fields.Many2one('fastra.leave.request', string="Leave Request Id")
    leave_type_id = fields.Many2one('fastra.leave.type', string="Type of Leave")
    leave_reasons = fields.Char("Use only Please state reasons")
    leave_duration = fields.Integer("Leave Duration")
    commencement_date = fields.Date("Commencement Date")
    resumption_date = fields.Date("Resumption Date")
    address_while_leave = fields.Char("Address while on Leave")
    telephone = fields.Char("Telephone No while on Leave")
    relif_employee_id = fields.Many2one("hr.employee", string="Name of Relief Staff")
    staff_sign = fields.Binary("Staff Signature")
    hod_sign = fields.Binary("HOD’s Approval & Signature")


class FastraLeaveType(models.Model):
    _name = 'fastra.leave.type'

    name = fields.Char("Name")
