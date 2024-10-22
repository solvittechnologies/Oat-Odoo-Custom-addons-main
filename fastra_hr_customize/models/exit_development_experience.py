from odoo import fields, models, api


class ExitDevelopmentExperience(models.Model):
    _name = 'exit.development.experience'
    _description = 'Exit Development Experience'

    name = fields.Char("Name")
