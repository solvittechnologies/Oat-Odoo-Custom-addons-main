# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
    )
    code = fields.Char("Code")

    @api.onchange('category_id')
    def _onchange_category_id(self):
        domain = {}
        if self.category_id:
            domain = {'product_id': [('categ_id', '=', self.category_id.id)]}
        else:
            domain = {'product_id': []}
        return {'domain': domain}
