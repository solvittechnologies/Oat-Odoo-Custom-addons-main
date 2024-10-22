from odoo import models, api, fields, _
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64
from io import BytesIO


class SkilledWorkers(models.Model):
    _name = 'skilled.workers'

    company_id = fields.Many2one('res.company', string="Company")
    week = fields.Char("Week")

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    staff_line_ids = fields.One2many('skilled.workers.staff.line', 'skilled_workers_id', string="Staff Lines")
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')

    def generate_excel(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Skill Workers Report')

        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})

        row = 0
        worksheet.write(row, 0, 'Company', format1)
        worksheet.write(row, 1, self.company_id and self.company_id.name or '')
        row += 1
        worksheet.write(row, 0, 'Week', format1)
        worksheet.write(row, 1, self.week or '')
        row += 1
        date_string = ""
        if self.date_from:
            date_string = "%s" % self.date_from.strftime('%m/%d/%Y')
            if self.date_to:
                date_string += "-%s" % self.date_to.strftime('%m/%d/%Y')
        worksheet.write(row, 0, 'Date From', format1)
        worksheet.write(row, 1, date_string)
        row += 1
        worksheet.write(row, 0, 'Location', format1)
        worksheet.write(row, 1, self.location_id and self.location_id.name or '')
        row += 2

        worksheet.write(row, 0, 'Staff', format1)
        worksheet.write(row, 1, 'Worker Department', format1)
        worksheet.write(row, 2, 'Saturday', format1)
        worksheet.write(row, 3, 'Sunday', format1)
        worksheet.write(row, 4, 'Monday', format1)
        worksheet.write(row, 5, 'Tuesday', format1)
        worksheet.write(row, 6, 'Wednesday', format1)
        worksheet.write(row, 7, 'Thursday', format1)
        worksheet.write(row, 8, 'Friday', format1)
        worksheet.write(row, 9, 'Saturday', format1)
        worksheet.write(row, 10, 'Comment', format1)
        worksheet.write(row, 11, 'Total Days Present', format1)
        worksheet.write(row, 12, 'Total Days Absent', format1)

        row += 1
        for line in self.staff_line_ids:
            worksheet.write(row, 0, line.staff_id and line.staff_id.name or '')
            worksheet.write(row, 1, line.worker_department_id and line.worker_department_id.name or '')
            worksheet.write(row, 2, line.saturday or '')
            worksheet.write(row, 3, line.sunday or '')
            worksheet.write(row, 4, line.monday or '')
            worksheet.write(row, 5, line.tuesday or '')
            worksheet.write(row, 6, line.wednesday or '')
            worksheet.write(row, 7, line.thursday or '')
            worksheet.write(row, 8, line.friday or '')
            worksheet.write(row, 9, line.saturday_2 or '')
            worksheet.write(row, 10, line.comment or '')
            worksheet.write(row, 11, line.total_days_present or '')
            worksheet.write(row, 12, line.total_days_absent or '')
            row += 1

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Skilled Workers Sheet.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=skilled.workers&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }


class SkilledWorkersStaffLine(models.Model):
    _name = 'skilled.workers.staff.line'

    staff_id = fields.Many2one('hr.employee', string="Staff")
    worker_department_id = fields.Many2one('hr.department', "Worker Department")
    saturday = fields.Boolean("Saturday")
    sunday = fields.Boolean("Sunday")
    monday = fields.Boolean("Monday")
    tuesday = fields.Boolean("Tuesday")
    wednesday = fields.Boolean("Wednesday")
    thursday = fields.Boolean("Thursday")
    friday = fields.Boolean("Friday")
    saturday_2 = fields.Boolean("Saturday")
    comment = fields.Text("Comment")
    total_days_present = fields.Integer("Total Days Present", compute="get_total_present_days")
    total_days_absent = fields.Integer("Total Days Absent", compute="get_total_absent_days")
    skilled_workers_id = fields.Many2one('skilled.workers', string="skilled workers")

    @api.multi
    @api.depends('saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday_2')
    def get_total_present_days(self):
        for rec in self:
            count = 0
            if rec.saturday or rec.saturday_2:
                count += 1
            if rec.monday:
                count += 1
            if rec.tuesday:
                count += 1
            if rec.wednesday:
                count += 1
            if rec.thursday:
                count += 1
            if rec.friday:
                count += 1
            rec.total_days_present = count

    @api.multi
    @api.depends('saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday_2')
    def get_total_absent_days(self):
        for rec in self:
            count = 0
            if not rec.monday:
                count += 1
            if not rec.tuesday:
                count += 1
            if not rec.wednesday:
                count += 1
            if not rec.thursday:
                count += 1
            if not rec.friday:
                count += 1
            if not rec.saturday and not rec.saturday_2:
                count += 1
            rec.total_days_absent = count

    @api.multi
    @api.onchange('staff_id')
    def onchange_staff_id(self):
        if self.staff_id:
            self.worker_department_id = self.staff_id.department_id
