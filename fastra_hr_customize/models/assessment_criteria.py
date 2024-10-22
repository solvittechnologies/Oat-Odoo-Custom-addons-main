from odoo import fields, models

class ASSESSMENTCRITERIA(models.Model):
    _name = 'assessment.criteria'

    name = fields.Char("ASSESSMENT CRITERIA")
    excellent = fields.Char("5 (EXCELLENT)")
    very_good = fields.Char("4 (VERY GOOD)")
    good = fields.Char("3 (GOOD)")
    poor = fields.Char("2 (POOR)")
    very_poor = fields.Char("1 (VERY POOR)")