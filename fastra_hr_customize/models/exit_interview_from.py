from odoo import fields, models, api


class ExitInterviewForm(models.Model):
    _name = 'exit.interview.form'

    name = fields.Char('Name')
    joining_date = fields.Date('Date of Joining')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)
    location_id = fields.Many2one('stock.location', string="Location")
    designation_id = fields.Many2one('stock.location', string="Designation")
    email = fields.Char('Email ID')
    exit_date = fields.Date('Date of Exit')

    other_important_info = fields.Text('Other Important Information')
    most_frustrating_aspect = fields.Text('Most Frustrating Aspect')
    most_satisfying_aspect = fields.Text('Most Satisfying Aspect')
    stay_back_with_organisation = fields.Text('Stay Back with Organisation')
    is_yes_return_dana_group = fields.Boolean("Yes")
    is_no_return_dana_group = fields.Boolean("No")
    is_yes_return_to_specific_subsidiary = fields.Boolean("Yes")
    is_no_return_to_specific_subsidiary = fields.Boolean("No")
    is_yes_recommend_to_friends = fields.Boolean("Yes")
    is_no_recommend_to_friends = fields.Boolean("No")
    major_strength_1 = fields.Char("Major Strength 1")
    major_strength_2 = fields.Char("Major Strength 2")
    major_strength_3 = fields.Char("Major Strength 3")
    major_improvement_area_1 = fields.Char("Major Improvement Area 1")
    major_improvement_area_2 = fields.Char("Major Improvement Area 2")
    major_improvement_area_3 = fields.Char("Major Improvement Area 3")
    is_fmcg_sale = fields.Boolean('FMCG Sales')
    is_hospitality = fields.Boolean('Hospitality')
    is_banking = fields.Boolean('Banking/Insurance')
    is_automobile = fields.Boolean('Automobile')
    is_manufacturing = fields.Boolean('manufacturing')
    is_it = fields.Boolean('IT/Telecom')
    is_engineering = fields.Boolean('Engineering')
    is_pharmaceutical = fields.Boolean('Pharmaceutical')
    is_other = fields.Boolean('Specify any other')
    other_join_reason = fields.Char("Other industry")
    new_company_designation_offer = fields.Char("New Company Designation Offer")
    is_less_10 = fields.Boolean("Less than 10%")
    is_10_15 = fields.Boolean("10-15%")
    is_15_20 = fields.Boolean("15-20%")
    is_20_25 = fields.Boolean("20-25%")
    is_25_30 = fields.Boolean("25-30%")
    is_above_30 = fields.Boolean("Above 30%")
    other_benefits_aside_salary = fields.Text("Other Benefits Aside Salary")
    interview_hr_id = fields.Char(string="Interview By")
    date = fields.Date("Date")

    return_resignation_ids = fields.One2many('return.resignation.line', 'exit_interview_form_id',
                                             string="Reason Resignation Line")
    exit_development_experience_ids = fields.One2many('exit.development.experience.line', 'exit_interview_form_id',
                                                      string="Exit Development Experience Line")
    general_work_culture_ids = fields.One2many('general.work.culture.line', 'exit_interview_form_id',
                                               string="Exit Development Experience Line")
    inter_personal_relation_ids = fields.One2many('inter.personal.relation.line', 'exit_interview_form_id',
                                                  string="Exit Development Experience Line")

    @api.model
    def default_get(self, fields):
        """ create the lines on the wizard """
        res = super(ExitInterviewForm, self).default_get(fields)

        lines = []
        exit_experience_lines = []
        reason_ids = self.env['resignation.reason'].search([])
        for reason in reason_ids:
            lines.append((0, 0, {
                'resignation_return_id': reason.id,
            }))
        experience_ids = self.env['exit.development.experience'].search([])
        for experience_id in experience_ids:
            exit_experience_lines.append((0, 0, {
                'exit_development_experience_id': experience_id.id,
            }))
        res['return_resignation_ids'] = lines
        res['exit_development_experience_ids'] = exit_experience_lines
        return res


class ReturnResignationLine(models.Model):
    _name = 'return.resignation.line'

    exit_interview_form_id = fields.Many2one('exit.interview.form', string="Exit Interview Form")
    resignation_return_id = fields.Many2one('resignation.reason', string="Reason")
    comment = fields.Char("Comment")
    is_yes = fields.Boolean("Yes")
    is_no = fields.Boolean("No")


class ExitDevelopmentExperienceLine(models.Model):
    _name = 'exit.development.experience.line'

    exit_interview_form_id = fields.Many2one('exit.interview.form', string="Exit Interview Form")
    exit_development_experience_id = fields.Many2one('exit.development.experience', string="Reason")
    comment = fields.Char("Comment")
    is_excellent = fields.Boolean("Excellent")
    is_very_good = fields.Boolean("Very Good")
    is_good = fields.Boolean("Good")
    is_poor = fields.Boolean("Poor")
    remarks = fields.Char("Remarks")


class GeneralWorkCultureLine(models.Model):
    _name = 'general.work.culture.line'

    exit_interview_form_id = fields.Many2one('exit.interview.form', string="Exit Interview Form")
    reason = fields.Char(string="Reason")
    comment = fields.Char("Comment")
    is_excellent = fields.Boolean("Excellent")
    is_very_good = fields.Boolean("Very Good")
    is_good = fields.Boolean("Good")
    is_poor = fields.Boolean("Poor")
    remarks = fields.Char("Remarks")


class InterpersonalRelationLine(models.Model):
    _name = 'inter.personal.relation.line'

    exit_interview_form_id = fields.Many2one('exit.interview.form', string="Exit Interview Form")
    reason = fields.Char(string="Reason")
    comment = fields.Char("Comment")
    is_excellent = fields.Boolean("Excellent")
    is_very_good = fields.Boolean("Very Good")
    is_good = fields.Boolean("Good")
    is_poor = fields.Boolean("Poor")
    remarks = fields.Char("Remarks")
