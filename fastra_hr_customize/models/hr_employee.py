from odoo import fields, models, api


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    employee_unique_code = fields.Char('Employee Code', copy=False)
    gross_monthly_pay = fields.Float("Gross Monthly Pay")
    account_details = fields.Char("Account Details")
    birth_date = fields.Date(string='Date Of Bith')
    date_of_employment = fields.Date(string='Date Of Employment')
    # leave_balance = fields.Integer('Leave Balance', compute="get_leave_balance")
    # absent_balance = fields.Integer('Absent', compute="get_absent_balance")

    # Big data fields
    full_name = fields.Char('NAME')
    gender = fields.Char('GENDER')
    maiden_name = fields.Char('MAIDEN NAME (If married female)')
    date_of_birth = fields.Date(string='DATE OF BIRTH')
    place_of_birth = fields.Char('PLACE OF BIRTH')
    nationality = fields.Char('NATIONALITY')
    state_of_origin = fields.Char('STATE OF ORIGIN (If Nigerian)')
    local_goverment = fields.Char('LOCAL GOVERNMENT')
    residential_address = fields.Text('RESIDENTIAL ADDRESS')
    permanent_home_address = fields.Text('PERMANENT HOME ADDRESS')
    telephone_number = fields.Char('TELEPHONE NUMBER')
    telephone_alternative = fields.Char('ALTERNATE')
    email = fields.Char('EMAIL')
    employee_institute_ids = fields.One2many('employee.institute', 'employee_id', string="Institute Lines")
    employee_education_ids = fields.One2many('employee.education', 'employee_id', string="Qualification Lines")
    marital_status = fields.Char('MARITAL STATUS')
    name_of_spouse = fields.Char('NAME OF SPOUSE')
    employee_child_ids = fields.One2many('employee.child', 'employee_id', string="Child Lines")
    employee_kin_ids = fields.One2many('employee.kin', 'employee_id', string="Kin Lines")
    employee_previous_ids = fields.One2many('employee.previous.data', 'employee_id', string="Previous Lines")
    employee_reference_ids = fields.One2many('employee.reference', 'employee_id', string="Reference Lines")
    signature = fields.Binary('SPECIMEN SIGNATURE', copy=False, attachment=True)
    signature_date = fields.Date("DATE")

    @api.model
    def create(self, values):
        res = super(HREmployee, self).create(values)
        reference_code = self.env['ir.sequence'].next_by_code('employee.unique.code')
        if res.company_id:
            res.employee_unique_code = res.company_id.employee_code_start + '/' + reference_code
        return res

    @api.multi
    def get_leave_balance_view(self):
        return

    @api.multi
    def get_absent_balance_view(self):
        return


class EmployeeInstitute(models.Model):
    _name = 'employee.institute'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char('INSTITUTION')
    date = fields.Date('DATE')


class EmployeeEducation(models.Model):
    _name = 'employee.education'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char('EDUCATIONAL QUALIFICATION')
    date = fields.Date('DATE')


class EmployeeChild(models.Model):
    _name = 'employee.child'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char('Name of Children (in full)')
    gender = fields.Char("Gender")
    date_of_birth = fields.Date('Date of Birth')


class EmployeeKin(models.Model):
    _name = 'employee.kin'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char('Name of Children (in full)')
    relationship = fields.Char("Relationship")
    address = fields.Char('Address')
    split_benefit = fields.Float("% Split for Benefits")


class EmployeePreviousDate(models.Model):
    _name = 'employee.previous.data'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    company_name = fields.Char('COMPANY NAME')
    company_address = fields.Char('COMPANY ADDRESS')
    designation_held = fields.Char('DESIGNATION HELD')
    from_date = fields.Date("From")
    to_date = fields.Date("To")


class EmployeeReference(models.Model):
    _name = 'employee.reference'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char("NAME")
    address = fields.Char("RESIDENTIAL ADDRESS")
    nearest_bus_stop = fields.Char('NEAREST BUS STOP')
    telephone = fields.Char("TELEPHONE NUMBER")
    email = fields.Char("EMAIL")
