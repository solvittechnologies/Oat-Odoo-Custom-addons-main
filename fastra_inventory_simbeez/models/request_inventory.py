# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class RequestInventory(models.Model):
    _name = 'request.inventory'
    _rec_name = "store_manager_id"

    @api.model
    def _get_default_approver(self):
        result = self.env['stock.location'].sudo().search([('store_keeper', '=', self.env.uid)])
        if len(result)>0:
            try: 
                return self.env['res.users'].browse(result.branch_manager.id)
            except:
                pass
        if len(result)<=0:
            result_store_keeper = self.env['stock.location'].search([('store_keeper', '=', self.env.uid)])
            if result_store_keeper:
                try:
                    return self.env['res.users'].browse(result_store_keeper.branch_manager.id)
                except:
                    pass

    @api.model
    def _get_default_location(self):
        result = self.env['stock.location'].sudo().search([('store_keeper', '=', self.env.uid)])
        if len(result)==1:
            return result.id
        if len(result)>1:
            return result[0].id

    store_manager_id = fields.Many2one("res.users", string='Store Keeper', default=lambda self: self.env.user)
    source_location_id = fields.Many2one('stock.location', string="Source Location",default=_get_default_location)
    request_date = fields.Date('Purchase Date', default=datetime.date(datetime.now()))
    receiver_user_id = fields.Many2one('res.users', String='Project Mangaer',default=_get_default_approver)
    destination_location_id = fields.Many2one('stock.location', string="Purchase Location",default=_get_default_location)
    #date_returned = fields.Date('Return Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approve', 'Approve')
    ], string='Status', index=True, default='draft', copy=False)
    request_line_ids = fields.One2many('request.inventory.line', 'request_inventory_id', string='Request Lines')
    expected_to_return = fields.Boolean('Expected To Return')

    @api.multi
    def submit_request(self):
        for record in self:
            for request_line_id in record.request_line_ids:
                if request_line_id.quantity > request_line_id.product_id.qty_available:
                    request_line_id.state = 'not_available'
                else:
                    request_line_id.state = 'available'
            record.write({'state': 'request'})

    @api.multi
    def reset_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_request_approve(self):
        self.request_approve()
        return 
        return {
            'name': _('Approval Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.confirm.req',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_inv_req_id':self.id
                }
        }

    @api.multi
    def request_approve(self,expected_to_return=False):
        stock_obj = self.env['stock.move'].sudo()
        new_state = "approve"
        for request_line_id in self.request_line_ids:
            stock_move_val = {'location_id': self.source_location_id.id,
                              'location_dest_id': self.destination_location_id.id,
                              'product_id': request_line_id.product_id.id,
                              'product_uom': request_line_id.product_id.uom_id.id,
                              'product_uom_qty': request_line_id.quantity,
                              'quantity_done':request_line_id.quantity,
                              'name':  self.store_manager_id.name + ': ' + request_line_id.product_id.name
                              }
            st_mv_id = stock_obj.create(stock_move_val)
            st_mv_id._action_confirm()
            st_mv_id._action_assign()
            st_mv_id._action_done()
            # update stock in stock quant
            current_stock_obj = self.env['stock.quant'].sudo().search([('location_id','=',self.destination_location_id.id),('product_id','=',request_line_id.product_id.id)])
            current_stock = current_stock_obj.quantity + request_line_id.quantity
            current_stock_obj.write({'quantity':current_stock})
        if expected_to_return:
            new_state = "to_be_returned"
            expected_to_return = True
        self.write({'state': new_state,'expected_to_return':expected_to_return})

    @api.multi
    def inventory_request_return(self):
        self.write({'state': 'returned'})
        
       


class RequestInventoryLine(models.Model):
    _name = 'request.inventory.line'

    request_inventory_id = fields.Many2one('request.inventory', string="Request Inventory")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float("Quantity Purchased", default=1, digits=dp.get_precision('Product Unit of Measure'))
    state = fields.Selection([('available', 'Available'), ('not_available', 'Not Available')], string='Status', index=True, copy=False)
    expected_to_return = fields.Boolean(related='request_inventory_id.expected_to_return',string='Expected to Return')
    description = fields.Text(string='Description')
    requestes_inventory = fields.Many2one('inventory.request', string="Request From Inventory")
    qty_to_return = fields.Float('Quantity to Return')
    
class RequestOfInventory(models.Model):
    _name = 'inventory.request'

    @api.multi
    def submit_request(self):
        for rec in self:
            rec.state_of_request = 'request'
            
    @api.model
    def _get_default_approver(self):
        result = self.env['stock.location'].sudo().search([('store_keeper', '=', self.env.uid)], limit=1)
        if len(result)>0:
            try:

                return self.env['res.users'].browse(result.branch_manager.id).id
            except:
                pass
        if len(result)<=0:
            result_store_keeper = self.env['stock.location'].search([('store_keeper', '=', self.env.uid)])
            print(result_store_keeper,"store keeper result......")
            if result_store_keeper:
                try:
                    return self.env['res.users'].browse(result_store_keeper.branch_manager.id)
                except:
                    pass

    @api.model
    def _get_default_location(self):
        result = self.env['stock.location'].search([('store_keeper', '=', self.env.uid), ('company_id', '=', self.env.user.company_id.id)])
        if len(result)==1:
            return result.id
        if len(result)>1:
            return result[0].id


    @api.multi
    def generate_bill(self):
        for rec in self:
            bill = self.env['account.move']
            bill_line = self.env['account.move.line']
            move_lines = []
            for line in rec.request_lines:
                vals = {
                    'ref': "Release Product",
                    'date': rec.released_date,
                    'journal_id': line.product_id.categ_id.property_stock_journal.id,
                }

                bill_id = bill.create(vals)
                rec.move_ids = [(4, bill_id.id)]
                
                move_lines.append({
                    'move_id': bill_id.id,
                    'name': line.product_id.name,
                    'account_id': line.product_id.categ_id.property_account_expense_categ_id.id,
                    'debit': abs(line.product_id.standard_price * line.quantity),
                })
                move_lines.append({
                    'move_id': bill_id.id,
                    'name': line.product_id.name,
                    'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
                    'credit': abs(line.product_id.standard_price * line.quantity),
                })

            bill_line.create(move_lines)
            

    @api.multi
    def action_request_approve(self):
        for rec in self:
            # rec.generate_bill()
            rec.state_of_request = 'approve'
            # update stock in stock quant
            for request_line_id in self.request_lines:
                current_stock_obj = self.env['stock.quant'].sudo().search([('location_id','=',self.source_location.id),
                                                                           ('product_id','=',request_line_id.product_id.id)], limit = 1)
                current_stock = current_stock_obj.quantity - request_line_id.quantity
                current_stock_obj.write({'quantity': current_stock})

                # update stock in stock quant
                destination_stock_id = self.env['stock.quant'].sudo().search(
                    [('location_id', '=', self.destination_location.id), ('product_id', '=', request_line_id.product_id.id)], limit=1)
                if destination_stock_id:
                    new_stock = destination_stock_id.quantity + request_line_id.quantity
                    destination_stock_id.write({'quantity': new_stock})
                else:
                    self.env['stock.quant'].sudo().create({
                        'product_id': request_line_id.product_id.id,
                        'location_id': self.destination_location.id,
                        'quantity': request_line_id.quantity,
                    })
          
    @api.multi
    def reset_to_draft(self):
        self.write({'state_of_request': 'draft'})
        
    def _get_destination_location(self):
        rvl_id = self.env['stock.location'].sudo().search([('name', '=', 'Raycon Virtual Location')], limit=1)
        if rvl_id:
            return rvl_id.id
        else:
            return False
        
    store_keeper_name = fields.Many2one("res.users", string='Store Keeper Name', default=lambda self: self.env.user)
    source_location = fields.Many2one('stock.location', string="Source Location",default=_get_default_location)
    Receiver_name = fields.Char(string="Receiver Name")
    released_date = fields.Date('Date Released', default=datetime.date(datetime.now()))
    Project_manager = fields.Many2one('res.users', String='Project Mangaer', default=_get_default_approver)
    destination_location = fields.Many2one('stock.location', string="Destination Location", default=_get_destination_location)
    state_of_request = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approve', 'Approve'),
        ('return_approve', 'Return Approve'),
        ('return', 'Return'),
    ], string='Status', index=True, default='draft', copy=False)
    request_lines = fields.One2many('request.inventory.line', 'requestes_inventory', string='Request Lines')
    move_ids = fields.Many2many('account.move')


    def action_get_account_moves(self):
        form_view = self.env.ref('account.view_move_form').id
        tree_view = self.env.ref('account.view_account_move_filter').id

        return {
            'name': _('Journal Entry'),
            'domain': [('id', 'in', self.move_ids.ids)],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'view_id': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        
        
    @api.multi
    def inventory_request_return(self):
        self.write({'state_of_request': 'return_approve'})

    
    @api.multi
    def action_request_return_approve(self):
        stock_obj = self.env['stock.move'].sudo()
        for request_line_id in self.request_lines:
            if request_line_id.qty_to_return:
                stock_move_val = {'location_id': self.destination_location.id,
                                  'location_dest_id': self.source_location.id,
                                  'product_id': request_line_id.product_id.id,
                                  'product_uom': request_line_id.product_id.uom_id.id,
                                  'qty_to_return': request_line_id.qty_to_return,
                                  'quantity_done':request_line_id.qty_to_return,
                                  'name':  self.store_keeper_name.name + ': ' + request_line_id.product_id.name
                                  }
                st_mv_id = stock_obj.create(stock_move_val)
                st_mv_id._action_confirm()
                st_mv_id._action_assign()
                st_mv_id._action_done()
                # update stock in stock quant
                current_stock_obj = self.env['stock.quant'].sudo().search([('location_id','=',self.source_location.id),('product_id','=',request_line_id.product_id.id)])
                current_stock = current_stock_obj.quantity + request_line_id.qty_to_return
                current_stock_obj.write({'quantity':current_stock})
        self.write({'state_of_request': 'return'})
         

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    date = fields.Date('Date', related="inventory_id.date")
    qty_stock = fields.Float('Quantity in Move', compute='get_on_hand_stock')
    qty_available = fields.Float('Quantity Available', compute='get_qty_available')
    inventory_valuation = fields.Float('Inventory Valuation', compute='get_inventory_valuation')
    unit_price = fields.Float("Unit Price", related='product_id.standard_price')

    @api.multi
    @api.depends('product_id', 'location_id')
    def get_on_hand_stock(self):
        for rec in self:
            rec.qty_stock = 0.0
            if rec.product_id:
                rec.qty_stock = rec.product_id.with_context({'location': rec.location_id.id}).qty_available

    @api.multi
    @api.depends('qty_stock', 'qty_to_consume')
    def get_qty_available(self):
        for rec in self:
            rec.qty_available = rec.qty_stock - rec.qty_to_consume

    @api.multi
    @api.depends('qty_stock', 'qty_to_consume')
    def get_inventory_valuation(self):
        for rec in self:
            rec.inventory_valuation = 0.0
            if rec.product_id:
                rec.inventory_valuation = rec.product_id.with_context({'location': rec.location_id.id}).qty_available * rec.product_id.standard_price

class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.multi
    def open_inventory_value(self):
        material_consumption_line_ids = self.env['stock.inventory.line'].search([('location_id', '=', self.id)])
        action = self.env.ref('fastra_inventory_simbeez.action_material_consumption_line_view').read()[0]
        action['domain'] = [('id', 'in', material_consumption_line_ids.ids)]
        return action


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    quantity_available = fields.Float("Quantity Available",compute="compute_quantity_available")
    inventory_value = fields.Float(string="Inventory Value",compute="compute_inventory_value")
    unit_price = fields.Float(related='product_id.lst_price',string="Unit Price")
    quantity_ordered = fields.Float(string="Quantity Ordered",compute="compute_quantity_ordered")

    @api.multi
    @api.depends('unit_price','qty_done')
    def compute_inventory_value(self):
        for rec in self:
            rec.inventory_value = rec.unit_price * rec.qty_done

    @api.multi
    def compute_quantity_ordered(self):
        for rec in self:
            rec.quantity_ordered = 0
            stock_quant_id = self.env['stock.inventory.line'].search([('product_id', '=', rec.product_id.id),('location_id','=',rec.location_dest_id.id)])
            for qunt_id in stock_quant_id:
                rec.quantity_ordered += qunt_id.qty_to_consume

    @api.multi
    @api.depends('quantity_ordered', 'qty_done')
    def compute_quantity_available(self):
        for rec in self:
            rec.quantity_available = rec.qty_done - rec.quantity_ordered
