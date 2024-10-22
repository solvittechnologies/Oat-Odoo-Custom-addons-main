from odoo import fields, models, api,_

Rates = [('1', 'Unsatisfactory'),
         ('2', 'Improvement Needed'),
         ('3', 'Meets Expectation'),
         ('4', 'Exceeds Expectation'),
         ('5', 'Exceptional')]


class ConfirmationEvaluation(models.Model):
    _name = 'hr.confirmation.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Confirmation Evaluation'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Name of Employee")
    reviewer_employee_id = fields.Many2one('hr.employee', string="Name of reviewer")
    date_of_employment = fields.Date("Date of Employment")
    date_of_evaluation = fields.Date("Date of Evaluation")
    time_evaluation_covers = fields.Integer("Time Evaluation Covers")
    person_evaluated_befor = fields.Boolean(string="Has this person being evaluated before")

    work_product_ids = fields.One2many('confirmation.evaluation.work.product', 'confiemation_evaluation_id', string="Work Product")
    dependability_ids = fields.One2many('confirmation.evaluation.dependability', 'confiemation_evaluation_id', string="DEPENDABILITY")
    cooperativeness_ids = fields.One2many('confirmation.evaluation.cooperativeness', 'confiemation_evaluation_id', string="COOPERATIVENESS")
    adaptability_ids = fields.One2many('confirmation.evaluation.adaptability', 'confiemation_evaluation_id', string="ADAPTABILITY")
    total_score_1 = fields.Integer("Total Score")

    communication_ids = fields.One2many('confirmation.evaluation.communication', 'confiemation_evaluation_id', string="COMMUNICATION")
    dm_ps_ids = fields.One2many('confirmation.evaluation.dm.ps', 'confiemation_evaluation_id', string="DECISION MAKING AND PROBLEM SOLVING")
    improvement_ids = fields.One2many('confirmation.evaluation.improvement', 'confiemation_evaluation_id', string="IMPROVEMENT")
    tools_materials_ids = fields.One2many('confirmation.evaluation.tools.materials', 'confiemation_evaluation_id', string="USE OF TOOLS AND MATERIALS")
    total_score_2 = fields.Integer("Total Score")

    example_problem_resolve = fields.Text("Give an example of one time this person encountered a problem and how he or she resolved it:")
    person_improvement = fields.Text("In what area (s) could this person improve?")
    person_excel = fields.Text("In what area does this person excel?")
    is_person_extra_training = fields.Boolean("Has this person received any extra training within the evaluation time period?")
    is_promotion_this_year = fields.Boolean("If a promotion opened up this year, would this person be considered?")
    person_goal = fields.Text("Please list below this person’s goals for the next evaluation period:")

    organizational_leadership_ids = fields.One2many('confirmation.evaluation.organizational.leadership', 'confiemation_evaluation_id', string="ORGANIZATIONAL LEADERSHIP")
    positional_leadership_ids = fields.One2many('confirmation.evaluation.positional.leadership', 'confiemation_evaluation_id', string="POSITIONAL LEADERSHIP")
    interpersonal_leadership_ids = fields.One2many('confirmation.evaluation.interpersonal.leadership', 'confiemation_evaluation_id', string="HUMAN’S AND INTERPERSONAL LEADERSHIP")
    professional_leadership_ids = fields.One2many('confirmation.evaluation.professional.leadership', 'confiemation_evaluation_id', string="PROFESSIONAL LEADERSHIP")
    relationship_management_ids = fields.One2many('confirmation.evaluation.relationship.management', 'confiemation_evaluation_id', string="RELATIONSHIP WITH MANAGEMENT")

    hr_person_improvement = fields.Text("In what area (s) could this person improve?")
    hr_person_excel = fields.Text("In what area does this person excel?")
    hr_is_person_extra_training = fields.Boolean("Has this person received any extra training within the evaluation time period?")
    hr_is_promotion_this_year = fields.Boolean("If a promotion opened up this year, would this person be considered?")


class ConfirmationEvaluationWorkProduct(models.Model):
    _name = 'confirmation.evaluation.work.product'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("WORK PRODUCT")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationDependability(models.Model):
    _name = 'confirmation.evaluation.dependability'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("DEPENDABILITY")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationCooperativeness(models.Model):
    _name = 'confirmation.evaluation.cooperativeness'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("COOPERATIVENESS")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationAdaptability(models.Model):
    _name = 'confirmation.evaluation.adaptability'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("ADAPTABILITY")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationCommunication(models.Model):
    _name = 'confirmation.evaluation.communication'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("COMMUNICATION")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationDMPS(models.Model):
    _name = 'confirmation.evaluation.dm.ps'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("DECISION MAKING AND PROBLEM SOLVING")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationImprovement(models.Model):
    _name = 'confirmation.evaluation.improvement'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("IMPROVEMENT")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationTM(models.Model):
    _name = 'confirmation.evaluation.tools.materials'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("USE OF TOOLS AND MATERIALS")
    rate = fields.Selection(Rates, string="Rate")


# Second tab
class ConfirmationEvaluationOrganizationalLeadership(models.Model):
    _name = 'confirmation.evaluation.organizational.leadership'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("ORGANIZATIONAL LEADERSHIP")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationPositionalLeadership(models.Model):
    _name = 'confirmation.evaluation.positional.leadership'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("POSITIONAL LEADERSHIP")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationInterpersonalLeadership(models.Model):
    _name = 'confirmation.evaluation.interpersonal.leadership'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("HUMAN’S AND INTERPERSONAL LEADERSHIP")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationProfessionalLeadership(models.Model):
    _name = 'confirmation.evaluation.professional.leadership'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("PROFESSIONAL LEADERSHIP")
    rate = fields.Selection(Rates, string="Rate")


class ConfirmationEvaluationRelationshipManagement(models.Model):
    _name = 'confirmation.evaluation.relationship.management'

    confiemation_evaluation_id = fields.Many2one("hr.confirmation.evaluation", string="Confirmation Evaluation")
    name = fields.Char("RELATIONSHIP WITH MANAGEMENT")
    rate = fields.Selection(Rates, string="Rate")