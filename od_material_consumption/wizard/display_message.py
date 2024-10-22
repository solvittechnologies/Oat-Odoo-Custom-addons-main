from odoo import models, fields, api, _

class DisplayMessage(models.TransientModel):
    _name = 'display.message'
    
    name = fields.Char("Message")