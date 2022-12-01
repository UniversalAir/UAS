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
    'name': 'Universalair Extension',
    'version': '16.0.0.1',
    'category': 'website',
    'summary': '',
    'description': '''Universalair Extension
    ''',
    'author': 'Narendra Chauahan - Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': [
        'website',
        'website_sale',
        'website_crm',
        'website_crm',
        'sale_product_configurator',
        'website_sale_comparison',
        'website_sale_wishlist',
        'website_sale_stock',
        'website_blog',
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/category.xml",
        "views/product.xml",
        ],
    'assets': {
        'web.assets_frontend': [

        ],
        'web.assets_backend': [
            'universal_extension/static/src/xml/**/*'
            'universal_extension/static/src/js/**/*'
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

