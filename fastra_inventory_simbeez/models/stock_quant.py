from odoo import models,fields,api


class Quant(models.Model):
    _inherit = 'stock.quant'

    inventory_value = fields.Float('Inventory Value', compute='_compute_inventory_value')

    @api.multi
    def _compute_inventory_value(self):
        for quant in self:
            if quant.company_id != self.env.user.company_id:
                # if the company of the quant is different than the current user company, force the company in the context
                # then re-do a browse to read the property fields for the good company.
                quant = quant.with_context(force_company=quant.company_id.id)
            quant.inventory_value = quant.product_id.standard_price * quant.quantity

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(Quant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'inventory_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_value = 0.0
                    for l in lines:
                        total_value += l.inventory_value
                    line['inventory_value'] = total_value
        return res

