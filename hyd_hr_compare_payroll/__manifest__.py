# -*- coding: utf-8 -*-
{
    'name': "Compare and monitor payroll variation",

    'summary': """ Compare payroll variation between two periods. """,

    'description': """
        This module is a tool to compare payroll and monitor when payroll
        is growing and why. It give you 2 possibility:

        1) Compare payroll rule and identify what rule change from the previous
           period and give you the variation

        2) Compare payroll rule employee by employee and give you which rule
           Change and for which employee. So you will know very quickly what
           change compare to the first payroll period.
    """,

    'author': "HyD Freelance",
    'website': "http://",
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],

    # always loaded
    'data': [
             # data
             # views
             "views/menus.xml",

             # reports
             "reports/compare_payroll_rule_report.xml",
             "reports/compare_payslip_employee_report.xml",

             # wizards
             "wizards/compare_payroll_rule_wiz_views.xml",
             "wizards/compare_payslip_employee_wiz_views.xml"
             ],

    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'price': 0,
    'currency': 'EUR',
    'images': ['static/images/main_screenshot.png']
}
