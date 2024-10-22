from odoo import fields, models, api


class ResignationReason(models.Model):
    _name = 'resignation.reason'
    _description = 'Resignation Reason'

    name = fields.Char("Reason")
