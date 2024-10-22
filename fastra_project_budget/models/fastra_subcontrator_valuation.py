from odoo import fields, models, api, _


class FastraSubcontratorValuation(models.Model):
    _name = 'fastra.subcontrator.valuation'
    _description = 'Fastra Subcontrator Valuation'

    name = fields.Char("Sub contractor/ Piece worker")
    company_id = fields.Many2one("res.company", string="Company", track_visibility='always')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,
                                  help='Utility field to express amount currency', store=True)
    company_partner_id = fields.Many2one("res.partner", related="company_id.partner_id")
    work_order_id = fields.Many2one("fastra.work.order", string="Work Order No")
    agree_contract_sum = fields.Integer("Agreed Contract Sums")
    contract_duration = fields.Char("Contract Duration")
    value_of_work_done = fields.Char("Value of work done(using Agree Rates)")

    line_ids = fields.One2many("fastra.subcontrator.valuation.line", "subcontractor_valuation_id", string="Lines")

    total = fields.Integer("Total")
    retention = fields.Integer("Less: Retention")
    balance_after_retention = fields.Integer("Balance After Retention")
    previous_payment = fields.Integer("Less: Previous Payment")
    amount_due = fields.Integer("Amount Due")

    state = fields.Selection([('draft', 'Draft'),
                              ('send_project_coordinator', 'Send to Project Coordinator'),
                              ('approve', 'Approved'),
                              ('reject', 'Reject')], string="State", default='draft', track_visibility='always')
    rejection_note = fields.Text("Rejection Note")

    @api.multi
    def send_to_project_coordinator(self):
        self.write({'state': 'send_project_coordinator'})

    @api.multi
    def approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def reject(self):
        action = {
            'name': _('Rejection Confirmation'),
            'view_mode': 'form',
            'res_model': 'fastra.subcontrator.valuation.reject',
            'view_id': self.env.ref('fastra_project_budget.view_fastra_subcontrator_valuation_reject_form').id,
            'type': 'ir.actions.act_window',
            'context': {'default_subcontractor_valuation_id': self.id},
            'target': 'new'
        }
        return action


class FastraSubcontratorValuationLine(models.Model):
    _name = 'fastra.subcontrator.valuation.line'
    _description = 'Fastra Subcontrator Valuation Line'

    subcontractor_valuation_id = fields.Many2one("fastra.subcontrator.valuation", string="Subscontractor Valuation")
    no = fields.Integer("S/N")
    name = fields.Char("Description")
    qty = fields.Integer("Qty")
    rate = fields.Integer("Rate")
    amount = fields.Integer("Amount", compute='get_amount_total')

    @api.multi
    @api.depends('qty', 'rate')
    def get_amount_total(self):
        for rec in self:
            rec.amount = rec.qty * rec.rate


class FastraSubcontratorValuationReject(models.TransientModel):
    _name = 'fastra.subcontrator.valuation.reject'

    note = fields.Text("Note")
    subcontractor_valuation_id = fields.Many2one("fastra.subcontrator.valuation", string="Subscontractor Valuation")

    def reject(self):
        self.subcontractor_valuation_id.write({'state': 'reject', 'rejection_note': self.note})
