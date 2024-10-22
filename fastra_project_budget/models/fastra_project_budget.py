from odoo import fields, models, api


class FastraProjectBudget(models.Model):
    _name = 'fastra.project.budget'
    _description = 'Fastra Project Budget'
    _rec_name = "analytic_account_id"

    analytic_account_id = fields.Many2one('account.analytic.account', string="Project")
    manager_id = fields.Many2one('hr.employee', string="Project Manager")
    budget_cost_amount = fields.Float("Budget Cost", compute="get_budget_cost_amount")
    actual_cost_amount = fields.Float("Actual Cost")
    net_cost_amount = fields.Float("Net Value", compute="get_net_cost_amount")
    date = fields.Date("Date")

    line_ids = fields.One2many("fastra.project.budget.line", "fastra_budget_id", string="Lines")
    cost_line_ids = fields.One2many("fastra.project.budget.cost.line", "fastra_budget_id", string="Cost Lines")

    @api.multi
    @api.depends('budget_cost_amount', 'actual_cost_amount')
    def get_net_cost_amount(self):
        for rec in self:
            rec.net_cost_amount = rec.budget_cost_amount - rec.actual_cost_amount

    @api.multi
    @api.depends('line_ids')
    def get_budget_cost_amount(self):
        for rec in self:
            rec.budget_cost_amount = sum(rec.line_ids.mapped('total'))

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id:
            line_ids = self.env['fastra.project.budget.line'].search([('analytic_account_id', '=', self.analytic_account_id.id)])
            self.line_ids = [(6, 0, line_ids.ids)]


class FastraProjectBudgetLine(models.Model):
    _name = 'fastra.project.budget.line'
    _description = 'Fastra Project Budget Line'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Project")
    fastra_budget_id = fields.Many2one("fastra.project.budget", string="Project Budget")
    item = fields.Integer("Item")
    prelims_category_id = fields.Many2one('prelims.category', string="Cost Code")
    category_id = fields.Many2one("fastra.project.budget.line.category", string="Category")
    subcategory_id = fields.Many2one("fastra.project.budget.line.subcategory", string="Subcategory")
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    qty = fields.Integer("Labor Qty")
    material_uom_id = fields.Many2one("uom.uom", string="Material Unit")
    material_uom_custom_id = fields.Many2one("fastra.project.budget.measure.unit", string="Material Unit")
    material_qty = fields.Integer("Material Qty")
    material_rate = fields.Integer("Material Rate")
    labor_rate = fields.Integer("Labor Rate")
    material_amount = fields.Integer("Material Amount", compute="get_material_amount")
    labor_amount = fields.Integer("Labor Amount", compute="get_labor_amount")
    specialize_worker = fields.Integer("Specialize Worker")
    total = fields.Integer("Total", compute="get_total")

    @api.multi
    @api.depends('qty', 'material_rate')
    def get_labor_amount(self):
        for rec in self:
            rec.labor_amount = rec.qty * rec.material_rate

    @api.multi
    @api.depends('material_qty', 'material_rate')
    def get_material_amount(self):
        for rec in self:
            rec.material_amount = rec.material_qty * rec.material_rate

    @api.multi
    @api.depends('material_amount', 'labor_amount', 'specialize_worker')
    def get_total(self):
        for rec in self:
            rec.total = rec.material_amount + rec.labor_amount + rec.specialize_worker



class FastraProjectBudgetLineCategory(models.Model):
    _name = 'fastra.project.budget.line.category'
    _description = 'Fastra Project Budget Line Category'

    name = fields.Char("Name")


class FastraProjectBudgetLineSubCategory(models.Model):
    _name = 'fastra.project.budget.line.subcategory'
    _description = 'Fastra Project Budget Line Subcategory'

    name = fields.Char("Name")


class FastraProjectBudgetMeasureUnitCategory(models.Model):
    _name = 'fastra.project.budget.measure.unit'
    _description = 'Fastra Project Budget Measure Unit'

    name = fields.Char("Name")


class ProjectBudgetCostLine(models.Model):
    _name = 'fastra.project.budget.cost.line'
    _description = 'Fastra Project Budget Cost Line'

    fastra_budget_id = fields.Many2one("fastra.project.budget", string="Project Budget")
    prelims_category_id = fields.Many2one('prelims.category', string="Cost Code")
    project_element_category_id = fields.Many2one('project.element.category', string="Category")
    subcategory_id = fields.Many2one('subcategory.subcategory', string="Sub-Category")
    description = fields.Char("Description")
    actual_material_qty = fields.Float("Actual Material Qty")
    actual_material_rate = fields.Float("Actual Material Rate")
    actual_material_amount = fields.Float("Actual Material Amount")
    actual_labor_amount = fields.Float("Actual Labor Amount")
    actual_subcontractor_amount = fields.Float("Actual Subcontractor Amount")
    total_actual_cost = fields.Float("Total Actual Cost", compute='get_total_actual_cost')
    budget_saving = fields.Float("Budget Savings")
    actual_saving = fields.Float("Actual Saving")

    @api.depends('actual_material_amount', 'actual_labor_amount', 'actual_subcontractor_amount')
    def get_total_actual_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_material_amount + rec.actual_labor_amount + rec.actual_subcontractor_amount


class Subcategory(models.Model):
    _name = 'subcategory.subcategory'
    _description = 'Subcategory'

    name = fields.Char()


class PrelimsCategory(models.Model):
    _name = 'prelims.category'
    _description = 'Prelims Categories'

    name = fields.Char(required=True)


class CostCodeDictionary(models.Model):
    _name = 'cost.code.dictionary'
    _description = 'Cost Code Dictionary'

    prelims_category_id = fields.Many2one('prelims.category', string="Cost Code")
    project_element_category_id = fields.Many2one('project.element.category', string="Category")
    subcategory_id = fields.Many2one('subcategory.subcategory', string="Sub-Category")
