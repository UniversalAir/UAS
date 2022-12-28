{
    'name': 'Sale_Order Design',
    'version': '15.0.0.22',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': ['base','sale','web'],
    'data': [
        # "security/ir.model.access.csv",
        "views/sale_order_report.xml",
        # "views/report_invoice_new.xml",
        ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}