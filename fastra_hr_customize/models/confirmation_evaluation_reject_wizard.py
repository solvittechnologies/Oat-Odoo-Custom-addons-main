from odoo import models, fields


class AuditlogAutovacuum(models.TransientModel):
    _name = 'confirmation.evaluation.reject'

    note = fields.Text("Note")
    hr_confirmation_evaluation_id = fields.Many2one('hr.confirmation.evaluation', string="HR Confirmation Evaluation")

    def reject(self):
        self.hr_confirmation_evaluation_id.write({'state': 'reject', 'rejection_note': self.note})
