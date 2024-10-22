# -*- coding: utf-8 -*-

{
    'name': 'Project Analysis Extends',
    'version': '12.0.1.0.0',
    'summary': 'Project Analysis Extends',
    'depends': ['project_analysis_auslind', 'kay_petty_cash', 'purchase_request_petty_cash'],
    'data': [
        'data/ir_module_category_data.xml',
        'data/work_order_sequence.xml',

        'security/ir.model.access.csv',
        'security/project_budget_security.xml',

        'views/fastra_project_analysis_budget.xml',
        'views/move.xml',
        'views/boq_lines.xml',
        'views/fastra_project_budget.xml',
        'views/fastra_work_order.xml',
        'views/fastra_subcontrator_valuation.xml',
        'views/fastra_material_summary.xml',
        'views/fastra_preliminaries.xml',
        'views/fastra_project_measure_unit.xml',
        'views/cost_code_dictionary.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': -1,
}
