from odoo import models, fields, api

class BOQLines(models.Model):
    _name = 'boq.lines'

    name = fields.Char("Description")
    quantity = fields.Integer("QTY")
    agreed_quantity = fields.Integer("Agreed QTY")
    unit = fields.Many2one('uom.uom',string="Unit")
    rate = fields.Float("Rate")
    amount = fields.Float("Amount")
    amount_agreed_qty = fields.Float("Amount(Agreed Qty)")
    project = fields.Many2one('account.analytic.account',string="Project")


