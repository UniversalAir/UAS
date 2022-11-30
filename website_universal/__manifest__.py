#    Author: Narendra Chauhan(<https://www.warlocktechnologies.com/>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Website Universal',
    'version': '16.0.0.1',
    'category': 'ThemeeCommerce',
    'summary': '',
    'description': '''Universalair Website
    ''',
    'author': 'Narendra Chauahan - Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': ['web','website','universalair_extension','website_crm','website_sale_wishlist'],
    'data': [
        "views/components.xml",
        "views/header.xml",
        "views/shop_pag.xml",
        "views/product_quick_view.xml",
        "views/shop_product.xml",
        ],
    'assets': {
        'web.assets_frontend': [
            "website_universal/static/src/scss/custom.scss",
            "website_universal/static/src/scss/style.scss",
            "website_universal/static/src/scss/comman.scss",
            "website_universal/static/src/scss/fonts.scss",
            "website_universal/static/src/lib/css/owl.carousel.min.css",
            "website_universal/static/src/js/comman_methods.js",
            "website_universal/static/src/js/swDropdownMenu.js",
            "website_universal/static/src/js/make_model_drop.js",
            "website_universal/static/src/js/subcategory.js",
            "website_universal/static/src/js/SwWishlist.js",
            "website_universal/static/src/js/ajaxCart.js",
            "website_universal/static/src/js/mobile_sidebar.js",
            "website_universal/static/src/js/core/mixins.js",
            "website_universal/static/src/js/QuickView.js",
            "website_universal/static/src/js/slider.js",
            "/website_universal/static/src/lib/js/owl.carousel.min.js"
            
        ],
        'web.assets_common':[
            "/website_universal/static/src/lib/jquery-ui.js",
            "/website_universal/static/src/lib/js/accounting.min.js",
            "/website_universal/static/src/lib/js/price-slider.min.js",
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

