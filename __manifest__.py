{
    'name': 'Equipment Loan Tracker',
    'version': '1.0',
    'category': 'Inventory/Local',
    'summary': 'Modul untuk mencatat peminjaman alat kantor/laboratorium',
    'description': 'Modul custom Odoo untuk manajemen peminjaman inventaris.',
    'depends': ['base', 'product', 'stock', 'account'],
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/equipment_item_views.xml',
        'views/equipment_loan_views.xml',
        'views/menu_views.xml',
        'report/loan_report.xml',
    ],
}