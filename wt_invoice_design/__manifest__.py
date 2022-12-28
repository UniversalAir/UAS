{
    'name': 'Invoice Design',
    'version': '16.0.0.22',
    'category': '',
    'summary': '',
    'description': '''
    ''',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': ['base','account','web'],
    'data': [
        "security/ir.model.access.csv",

        # "data/"
        
        "views/res_company_view.xml",
        "views/report_invoice_new.xml",
        ],

    'assets':{
        # "web.assets_frontend":[
        #     '/website_design/static/src/scss/login_page.scss',
        #     '/website_design/static/src/scss/signup_page.scss',
        #     '/website_design/static/src/scss/reset_password_page.scss',
        #     '/website_design/static/src/scss/my_profile_page.scss',
        #     '/website_design/static/src/scss/invoice&bills_page.scss',
        #     '/website_design/static/src/scss/sale_order_page.scss',
        # ],
    },
    
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'external_dependencies': {
    },
}