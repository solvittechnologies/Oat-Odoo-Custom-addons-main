from odoo import fields, models, api


class FastraPreliminaries(models.Model):
    _name = 'fastra.preliminaries'
    _description = 'Fastra Preliminaries'
    _rec_name = 'project_id'

    project_id = fields.Many2one('account.analytic.account', string="Project")
    project_manager_id = fields.Many2one('hr.employee', string="Project Manager")
    date = fields.Date("Date")
    line_ids = fields.One2many("fastra.preliminaries.line", "preliminaries_id", string="Lines")
    summary_line_ids = fields.One2many("fastra.preliminaries.summary", "preliminaries_id", string="Summary Lines")


class FastraPreliminariesLine(models.Model):
    _name = 'fastra.preliminaries.line'

    preliminaries_id = fields.Many2one('fastra.preliminaries', string="Preliminary")
    name = fields.Char("Description")
    qty = fields.Integer("Qty")
    unit_id = fields.Many2one('uom.uom', string="Unit")
    rate = fields.Integer("Rate")
    amount = fields.Integer("Amount",compute='get_amount_total')

    @api.multi
    @api.depends('qty', 'rate')
    def get_amount_total(self):
        for rec in self:
            rec.amount = rec.qty * rec.rate


class FastraPreliminariesSummary(models.Model):
    _name = 'fastra.preliminaries.summary'
    _description = 'Fastra Preliminaries Summary'

    name = fields.Char("Summary")
    preliminaries_id = fields.Many2one('fastra.preliminaries', string="Preliminary")


