from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_code_start = fields.Char('Employee Code Start With')