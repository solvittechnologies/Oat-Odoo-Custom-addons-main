from odoo import models, api, fields, _
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64
from io import BytesIO


class OvertimeGuide(models.Model):
    _name = 'overtime.guide'

    company_id = fields.Many2one('res.company', string="Company")
    week = fields.Char("Week")
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    overtime_guide_line_ids = fields.One2many('overtime.guide.line', 'overtime_guide_id', string="Staff Lines")
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')

    def generate_excel(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Overtime Guide Report')

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

        worksheet.write(row, 0, 'Name', format1)
        worksheet.write(row, 1, 'Designation', format1)
        worksheet.write(row, 2, 'Day', format1)
        worksheet.write(row, 3, 'Remarks', format1)
        worksheet.write(row, 4, 'Amount', format1)

        row += 1
        for line in self.overtime_guide_line_ids:
            worksheet.write(row, 0, line.name and line.name.name or '')
            worksheet.write(row, 1, line.designation or '')
            worksheet.write(row, 2, line.day or '')
            worksheet.write(row, 3, line.remarks or '')
            worksheet.write(row, 4, line.amount or '')
            row += 1

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Overtime Guide Sheet.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=overtime.guide&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }


class OvertimeGuideLine(models.Model):
    _name = 'overtime.guide.line'

    name = fields.Many2one('hr.employee', string="Name")
    designation = fields.Char("Designation")
    day = fields.Char("Day")
    remarks = fields.Char("Remarks")
    amount = fields.Integer("Amount")
    overtime_guide_id = fields.Many2one('overtime.guide',string="Overtime Guide")

    @api.onchange('name')
    def onchange_name(self):
        self.designation = ''
        if self.name and self.name.work_location:
            self.designation = self.name.work_location