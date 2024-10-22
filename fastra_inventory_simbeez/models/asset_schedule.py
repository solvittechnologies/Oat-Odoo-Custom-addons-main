from odoo import models, fields, api,_


class AssetSchedule(models.Model):
    _name = 'asset.schedule'
    _description = 'Asset Schedule'

    product_id = fields.Many2one('product.product',string='Description')
    code = fields.Char(string='Code')
    opening_qty = fields.Float(string='Opening Quantity')
    qty_in = fields.Float(string='Quantity In')
    qty_out = fields.Float(string='Quantity Out')
    closing_qty = fields.Float(string='Closing Quantity', compute='_compute_closing_qty', store=True)
    status = fields.Char(string='Status')
    remarks = fields.Char(string='Remarks')

    @api.depends('opening_qty', 'qty_in', 'qty_out')
    def _compute_closing_qty(self):
        for record in self:
            record.closing_qty = record.qty_in - record.qty_out

    @api.model
    def get_repport_data(self):
        self._cr.execute("DELETE FROM asset_schedule")
        purchase_order_lines =self.env['purchase.order.line'].search([('category_id.name','=','Assets'),('state','=','purchase')])

        for lines in purchase_order_lines:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', lines.product_id.id),
                ('location_id', '=', lines.order_id.location_id.id),
            ])
            total_qty = sum(quant.quantity for quant in quants)

            getdata = self.env['request.inventory.line'].search([('product_id','=',lines.product_id.id),
                                                                 ('product_category_id.name','=','Assets'),
                                                                 ('requestes_inventory.state_of_request','=','approve')])
            total_asset_out_qty = sum(quant.quantity for quant in getdata)
            self.create({'product_id':lines.product_id.id,
                         'code':lines.code,
                         'opening_qty':total_qty,
                         'qty_in':lines.product_qty,
                         'status':'Done',
                         'qty_out':total_asset_out_qty
                         })

        action = {
            'name': (_('Asset Schedule')),
            'type': 'ir.actions.act_window',
            'res_model': 'asset.schedule',
            'view_mode': 'tree',

        }
        return action

class UpdayeInvRequest(models.Model):
    _inherit = 'request.inventory.line'

    def get_product_category(self):
        category_id = self.env['product.category'].search([('name', '=', 'Assets')], limit=1)
        return category_id.id

    product_category_id = fields.Many2one('product.category', string='Product category', default=get_product_category)
    code = fields.Char(string='Code')

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        return {
            'domain': {
                'product_id':[('categ_id', '=', self.product_category_id.id)]  if self.product_category_id  else [],
            }
        }
