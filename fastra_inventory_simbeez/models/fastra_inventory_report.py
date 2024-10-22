from odoo import models, fields, api,_

class FastraInventoryReport(models.Model):
    _name = 'fastra.inventory.report'

    date = fields.Date("Date")
    product_id = fields.Many2one('product.product',string="Product")
    description = fields.Text("Description")
    unit_price = fields.Float("Unit Price")
    qty_stock = fields.Float("Quantity in Stock")
    inventory_valuation = fields.Float("Inventory Valuation")
    qty_to_consume = fields.Float("Quantity Ordered")
    location_id = fields.Many2one('stock.location',string="Location")

