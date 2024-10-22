from odoo import fields, models, api
from datetime import datetime
import calendar
class TrainingPlans(models.Model):
    _name = 'training.plans'

    months = fields.Selection([('Jan', 'January'),
                               ('Feb', 'February'),
                               ('Mar', 'March'),
                               ('Apr', 'April'),
                               ('May', 'May'),
                               ('Jun', 'June'),
                               ('Jul', 'July'),
                               ('Aug', 'August'),
                               ('Sep', 'September'),
                               ('Oct', 'October'),
                               ('Nov', 'November'),
                               ('Dec', 'December'), ], string="Months")
    name_of_organizer = fields.Many2one('hr.employee', string="Name of organizer")
    location = fields.Many2one('stock.location', string="Location")
    training_plans_line_ids =fields.One2many('training.plans.lines','training_plan_id',string="Training Plans Line")
    date = fields.Date("Date")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)

    @api.multi
    @api.onchange('date')
    def onchange_date_of_month_selection(self):
        if self.date:
            month = self.date.strftime('%b')
            self.months = month

class TrainingPlans(models.Model):
    _name = 'training.plans.lines'

    serial_no = fields.Integer("SN")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    training_topic = fields.Char("Training Topic (for September)")
    staff_name = fields.Many2one('hr.employee', string="Name of Staff")
    staff_designation = fields.Many2one('hr.job',"Designation of Staff")
    trainer_name = fields.Many2one('hr.employee', string="Name of Trainer")
    trainer_designation = fields.Many2one('hr.job', "Designation of Trainer")
    trainer_objective = fields.Char("Objective / Contents of the training")
    budgeted = fields.Selection([('yes', 'Yes'),('no', 'No')], string="Budgeted")
    itf_Registered = fields.Char("ITF Registered")
    in_the_training_calender = fields.Selection([('yes', 'Yes'),('no', 'No')], string="in the Training calender")
    nos_of_participants = fields.Char("Nos of participants")
    certificate_issue = fields.Char("Certificate issue")
    training_plan_id = fields.Many2one('training.plans',string="Training Plan Id")

    @api.multi
    @api.onchange('staff_name')
    def onchange_staff(self):
        if self.staff_name:
            self.staff_designation = self.staff_name.job_id and self.staff_name.job_id.id or False

    @api.multi
    @api.onchange('trainer_name')
    def onchange_trainer_name(self):
        if self.trainer_name:
            self.trainer_designation = self.trainer_name.job_id and self.trainer_name.job_id.id or False