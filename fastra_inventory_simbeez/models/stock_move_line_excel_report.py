from odoo import models,fields, api, _
from odoo.tools.misc import xlsxwriter
import base64
from io import BytesIO


class StockMoveLineReportConfirm(models.TransientModel):
    _name = "stock.move.line.excel.report.confirm"

    file_name =fields.Char("File Name")
    excel_file = fields.Binary('Excel File')

    @api.multi
    def generate_excel_report(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Product Inventory Report')
        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})
        lien_ids = self.env['stock.move.line'].browse(active_ids[0])
        worksheet.write(0, 0, lien_ids.location_dest_id.display_name, bold)
        row = 1
        worksheet.write(row, 0, 'Date', format1)
        worksheet.write(row, 1, 'Product', format1)
        worksheet.write(row, 2, 'From', format1)
        worksheet.write(row, 3, 'To', format1)
        worksheet.write(row, 4, 'Quantity in Stock', format1)
        worksheet.write(row, 5, 'Unit Of Measure', format1)
        worksheet.write(row, 6, 'Quantity Available', format1)
        worksheet.write(row, 7, 'Quantity Ordered', format1)
        for record in self.env['stock.move.line'].browse(active_ids):
            row = row+1
            worksheet.write(row, 0, record.date.strftime("%m/%d/%Y, %H:%M:%S") or '')
            worksheet.write(row, 1, record.product_id.name or '')
            worksheet.write(row, 2, record.location_id.display_name or '')
            worksheet.write(row, 3, record.location_dest_id.display_name or '')
            worksheet.write(row, 4, record.qty_done or '')
            worksheet.write(row, 5, record.product_uom_id.name or '')
            worksheet.write(row, 6, record.quantity_available or '')
            worksheet.write(row, 7, record.quantity_ordered or '')

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodebytes(file_data.read()),
             'file_name': 'Product Inventory Report.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=stock.move.line.excel.report.confirm&id=" + str(
                self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }
