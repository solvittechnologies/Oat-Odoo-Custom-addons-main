from odoo import fields, models, api


class FastraWorkOrder(models.Model):
    _name = 'fastra.work.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Fastra Work Order'

    name = fields.Char("W.O. #")
    date = fields.Date("W.O. Date", track_visibility='always')
    partner_id = fields.Many2one("res.partner", string="Customer/Vendor", track_visibility='always')
    customer_id = fields.Char("Customer ID", track_visibility='always')
    category_id = fields.Many2one("fastra.project.budget.line.category", string="Category", track_visibility='always')
    category_text = fields.Char("Text", track_visibility='always')
    company_id = fields.Many2one("res.company", string="Company", track_visibility='always')
    company_partner_id = fields.Many2one("res.partner", related="company_id.partner_id")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,
                                  help='Utility field to express amount currency', store=True)
    job = fields.Char("Job", track_visibility='always')
    scope = fields.Integer("Scope", track_visibility='always')
    rate = fields.Integer("Rate", track_visibility='always')
    contract_sum = fields.Integer("Contract Sum", compute="get_contract_sum")
    additional_details = fields.Text("Additional Details", track_visibility='always')

    line_a_ids = fields.One2many("fastra.work.order.line.a", "work_order_id", string="Line A")
    line_b_ids = fields.One2many("fastra.work.order.line.b", "work_order_id", string="Line B")
    comment_line_ids = fields.One2many("fastra.work.order.line.comment", "work_order_id", string="Comment Lines")

    advance_material_cost = fields.Integer("Advance Plus Material Cost", track_visibility='always')
    previous_payment = fields.Integer("Previous Payment", track_visibility='always')
    amount_due = fields.Integer("Amount Due", compute='get_amount_due')

    state = fields.Selection([('draft', 'Draft'),
                              ('send_subcontractor', 'Send to Subcontractor'),
                              ('send_project_coordinator', 'Send to Project Coordinator'),
                              ('approve', 'Approved')], string="State", default='draft', track_visibility='always')

    @api.multi
    @api.depends('advance_material_cost', 'previous_payment')
    def get_amount_due(self):
        for rec in self:
            rec.amount_due = rec.advance_material_cost - rec.previous_payment

    @api.multi
    @api.depends('rate', 'scope')
    def get_contract_sum(self):
        for rec in self:
            rec.contract_sum = rec.rate * rec.scope

    @api.model
    def create(self, values):
        res = super(FastraWorkOrder, self).create(values)
        reference_code = self.env['ir.sequence'].next_by_code('fastra.work.order.code')
        res.name = reference_code
        return res

    @api.multi
    def send_to_subcontractor(self):
        self.write({'state': 'send_subcontractor'})

    @api.multi
    def send_to_project_coordinator(self):
        self.write({'state': 'send_project_coordinator'})

    @api.multi
    def approve(self):
        self.write({'state': 'approve'})


class FastraWorkOrderLineA(models.Model):
    _name = 'fastra.work.order.line.a'
    _description = 'Fastra Work Order Line A'

    work_order_id = fields.Many2one('fastra.work.order', string="Work Order")
    name = fields.Char("Service")
    qty = fields.Integer("Qty")
    completed = fields.Integer("% Completed")
    rate = fields.Integer("Rate")
    total = fields.Integer("Line Total", compute="get_total")

    @api.multi
    @api.depends('rate', 'qty')
    def get_total(self):
        for rec in self:
            rec.total = rec.qty * rec.rate


class FastraWorkOrderLineB(models.Model):
    _name = 'fastra.work.order.line.b'
    _description = 'Fastra Work Order Line B'

    work_order_id = fields.Many2one('fastra.work.order', string="Work Order")
    name = fields.Char("Initial Materials")
    qty = fields.Integer("Qty")
    unit_price = fields.Integer("Unit Price")
    total = fields.Integer("Line Total", compute="get_total")

    @api.multi
    @api.depends('unit_price', 'qty')
    def get_total(self):
        for rec in self:
            rec.total = rec.qty * rec.unit_price


class FastraWorkOrderLineComments(models.Model):
    _name = 'fastra.work.order.line.comment'
    _description = 'Fastra Work Order Line Comments'

    work_order_id = fields.Many2one('fastra.work.order', string="Work Order")
    name = fields.Char("Other Comments")
