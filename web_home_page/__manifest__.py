{
    'name': 'Website Home Page',
    'version': '16.0.0.1',
    'category': 'website',
    'summary': '',
    'description': '''
    ''',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': ['website'],
    'data': [
        'views/homepage.xml',
        'views/components.xml',
        ],
    'assets': {
        'web.assets_frontend': [
            '/web_home_page/static/src/lib/css/owl.carousel.min.css',
            '/web_home_page/static/src/lib/js/owl.carousel.min.js',
            '/web_home_page/static/src/css/carousal.css',
            '/web_home_page/static/src/scss/fonts.scss',
            '/web_home_page/static/src/scss/comman.scss',
            '/web_home_page/static/src/scss/style.scss',
            '/web_home_page/static/src/scss/header.scss',
            '/web_home_page/static/src/scss/custom.scss',
            '/web_home_page/static/src/scss/caourosel.scss',
            '/web_home_page/static/src/js/QuickViewDialog.js',
            '/web_home_page/static/src/js/comman_methods.js',
            '/web_home_page/static/src/js/swDropdownMenu.js',
            '/web_home_page/static/src/js/swSubCategory.js',
            '/web_home_page/static/src/js/slider.js',
            '/web_home_page/static/src/js/SwWishlist.js',
            '/web_home_page/static/src/js/ajaxCart.js',
            '/web_home_page/static/src/js/mobile_sidebar.js',
            '/web_home_page/static/src/js/make_model_drop.js',
            '/web_home_page/static/src/xml/quick_views.xml',     
        ],

        'web.assets_common': [
            '/web_home_page/static/src/lib/jquery-ui.js',
            '/web_home_page/static/src/lib/js/accounting.min.js',
            '/web_home_page/static/src/lib/js/price-slider.min.js'
        ],
    },

    
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'external_dependencies': {
    },

}