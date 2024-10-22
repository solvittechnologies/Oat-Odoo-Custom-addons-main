from odoo import models, api, fields, _
from odoo.tools.misc import xlsxwriter
import base64
from io import BytesIO

class TrainingFeedbackForm(models.Model):
    _name = 'training.feedback.form'

    name = fields.Many2one('hr.employee', string="Name")
    designation = fields.Many2one('hr.job',string="Designation")
    location = fields.Many2one('stock.location', string="Location")
    did_the_course_meet = fields.Selection([('not_met', 'Not Met'), ('fully_met', 'Fully met')], string="Did the course meet your learning objectives?")
    how_was_the_duration_of_the_course = fields.Selection(
        [('too_short', 'Too short. Couldn’t learn enough in such a short time'), ('just_fine', 'Just fine'), ('too_long', 'Too long. The concepts could be learned in much less time')], string="How was the duration of the course?")
    how_helpful_were_the_instructional_materials = fields.Selection(
        [('Not helpful', 'Not helpful. Made things more difficult to learn and understand'), ('really_made_things_easier', 'Really made things easier to understand and learn')], string="How helpful were the instructional materials?")
    will_you_recommend_this_materials_to_others = fields.Selection(
        [('no', 'No'), ('yes', 'Yes')], string="Will you recommend this materials to others?")

    rate_the_overall_training = fields.Selection(
        [('not_enough', 'Not enough for my own technical experience'), ('more_than_enough', 'More than enough for my own experience'),
         ('learnt_something_new', 'Learnt something new')], string="How would you rate the overall training?")

    the_facilitators_oral_explanations_to_the_lecture_materials = fields.Selection(
        [('excellent', 'Excellent'), ('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')], string="How would you rate the Facilitators oral explanations to the lecture materials?")

    instructor_answer_questions_from_the_audience = fields.Selection(
        [('poorly', 'Poorly'), ('answered_very_well', 'Answered very well to questions from the audience')], string="How well did the instructor answer questions from the audience?")

    after_training_you_can_handle_the_assigned_task = fields.Selection(
        [('yes', 'Yes'), ('no', 'No'),('not_relevant', 'Not relevant')], string="After this training, do you think you can handle the assigned task? (i.e) perform the functions as trained.")

    note = fields.Text("Any other comments and suggestions:")
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)

    @api.multi
    @api.onchange('name')
    def onchange_name_set_value(self):
        self.designation = self.name.job_id.id

    def generate_excel(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Training Feedback Form')
        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})

        row = 0
        worksheet.write(row, 0, 'Name', bold)
        worksheet.write(row, 1, self.name or '')

        worksheet.write(1, 0, 'Designation', bold)
        worksheet.write(1, 1, self.designation or '')

        worksheet.write(2, 0, 'Location', bold)
        worksheet.write(2, 1, self.location or '')

        worksheet.write(4, 0, 'Did the course meet your learning objectives?', bold)
        worksheet.write(4, 1, dict(self._fields['did_the_course_meet'].selection).get(self.did_the_course_meet) or '')

        worksheet.write(5, 0, 'How was the duration of the course?', bold)
        worksheet.write(5, 1, dict(self._fields['how_was_the_duration_of_the_course'].selection).get(self.how_was_the_duration_of_the_course) or '')

        worksheet.write(6, 0, 'How helpful were the instructional materials?', bold)
        worksheet.write(6, 1, dict(self._fields['how_helpful_were_the_instructional_materials'].selection).get(self.how_helpful_were_the_instructional_materials) or '')

        worksheet.write(7, 0, 'Will you recommend this materials to others?', bold)
        worksheet.write(7, 1, dict(self._fields['will_you_recommend_this_materials_to_others'].selection).get(self.will_you_recommend_this_materials_to_others) or '')

        worksheet.write(8, 0, 'How would you rate the overall training?', bold)
        worksheet.write(8, 1, dict(self._fields['rate_the_overall_training'].selection).get(self.rate_the_overall_training) or '')

        worksheet.write(9, 0, 'How would you rate the Facilitators oral explanations to the lecture materials?', bold)
        worksheet.write(9, 1, dict(self._fields['the_facilitators_oral_explanations_to_the_lecture_materials'].selection).get(self.the_facilitators_oral_explanations_to_the_lecture_materials) or '')

        worksheet.write(10, 0, 'How well did the instructor answer questions from the audience?', bold)
        worksheet.write(10, 1, dict(self._fields['instructor_answer_questions_from_the_audience'].selection).get(self.instructor_answer_questions_from_the_audience) or '')

        worksheet.write(11, 0, 'After this training, do you think you can handle the assigned task? (i.e) perform the functions as trained.', bold)
        worksheet.write(11, 1, dict(self._fields['after_training_you_can_handle_the_assigned_task'].selection).get(self.after_training_you_can_handle_the_assigned_task) or '')

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Training Feedback Form.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=training.feedback.form&id=" + str(
                self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }