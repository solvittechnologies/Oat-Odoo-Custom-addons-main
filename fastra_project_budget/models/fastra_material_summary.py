from odoo import fields, models, api


class FastraMaterialSummary(models.Model):
    _name = 'fastra.material.summary'
    _description = 'Fastra Material Summary'

    name = fields.Char("Description")
    qty = fields.Integer("Qty")
    rate = fields.Integer("Rate")
    amount = fields.Integer("Amount", compute="get_amount_total")
    unit_id = fields.Many2one('uom.uom', string="Unit")
    remark = fields.Char("Remarks")

    @api.multi
    @api.depends('qty', 'rate')
    def get_amount_total(self):
        for rec in self:
            rec.amount = rec.rate * rec.qty
