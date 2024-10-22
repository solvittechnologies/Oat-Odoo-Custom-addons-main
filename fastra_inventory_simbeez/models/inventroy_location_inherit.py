from odoo import models,fields,api

class InventoryLocationInherit(models.Model):
    _inherit = 'stock.location'

    def get_inventory_value(self):
        line_id = self.env['stock.inventory.line'].search([('location_id', '=', self.id)])
        print(line_id)
