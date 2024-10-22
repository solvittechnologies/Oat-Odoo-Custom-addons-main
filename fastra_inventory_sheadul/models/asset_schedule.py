from odoo import api, fields, models

class UpdayeInvRequest(models.Model):
    _inherit = 'request.inventory.line'

    product_category_id = fields.Many2one('product.category', string='Product category')
    code = fields.Char(string='Code')

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        return {
            'domain': {
                'product_id':[('categ_id', '=', self.product_category_id.id)]  if self.product_category_id  else [],
            }
        }
    @api.model
    def get_repport_data(self):
        getdata=self.env['request.inventory.line'].search([])
        data=[]
        for d in getdata:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', d.product_id.id),
                ('location_id', '=', d.request_inventory_id.source_location_id.id),
            ])
            total_qty = sum(quant.quantity for quant in quants)
            dataobjt={
                "id":d.id,
                "description":d.description,
                "code":d.code,
                "opening_qty":total_qty,
                "qty_in":0,
                "qty_out":0,
                "closing_qty":d.product_id.qty_available,
                "status":d.request_inventory_id.state,
                "remarck":""
            }

            data.append(dataobjt)
        return data

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    product_category_id = fields.Many2one('product.category', string='Product Category')

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        return {
            'domain': {
                'product_id':[('categ_id', '=', self.product_category_id.id)]  if self.product_category_id  else [],
            }
        }