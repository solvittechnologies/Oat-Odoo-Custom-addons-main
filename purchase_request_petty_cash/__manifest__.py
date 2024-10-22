
{
    "name": "Purchase Request Petty Cash",
    "category": "Purchase Management",
    "depends": [
        "purchase_request",
        'kay_petty_cash',
        "account",
        "hr"
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/petty_cash_security.xml',
        'security/rules.xml',
        'wizard/cancel_reason_view.xml',
        
        'views/petty_cash.xml',
        'views/account_invoice.xml',
        'views/po_invoice.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
