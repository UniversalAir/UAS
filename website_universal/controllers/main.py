# -*- coding: utf-8 -*-
import hashlib
import json

from odoo import http, fields
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute 
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from werkzeug.exceptions import Forbidden, NotFound
from odoo.osv import expression

class WebsiteSaleCustom(WebsiteSale):
	@http.route(['''/widgets/listing/getCategory/categoryId/<int:category_id>''',
		'''/widgets/listing/getCategory/categoryId/<string:category_id>'''
		], type='json', auth="public", website=True, csrf=False)
	def sidebar_categories(self, category_id=None):
		if category_id != 'main':
			category = request.env['product.public.category'].browse(int(category_id))
			res = request.env["ir.ui.view"]._render_template('website_universal.shop_department_main_tmpl', values={
				'selected_category_id': category or False,
			})
			return res
		if category_id == 'main':
			res = request.env["ir.ui.view"]._render_template('website_universal.shop_department_main_tmpl', values={
				'selected_category_id': False,
			})
			return res
		return False
	
	@http.route('/fetch/make/models', type='json', auth="public", methods=['POST'], website=True, csrf=False)
	def make_models(self, **kwargs):
		values = {
			'datas': None
		}
		templ = None
		if kwargs.get('make_id'):
			category = request.env['product.public.category'].browse(kwargs.get('make_id'))
			res = request.env["ir.ui.view"]._render_template('website_universal.make_sub_cate_id', values={
						'make_main_cate_id': category,
					})
			values['datas'] = res
		else:
			res = request.env["ir.ui.view"]._render_template('website_universal.make_sub_cate_id', {'make_main_cate_id': False})
			values['datas'] = res
		return values


	@http.route([
		'/shop',
		'/shop/page/<int:page>',
		'/shop/category/<model("product.public.category"):category>',
		'/shop/category/<model("product.public.category"):category>/page/<int:page>',
	], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
	def shop(self, page=0, category=None, search='',min_price=0.0, max_price=0.0, ppg=21, **post):
		response = super(WebsiteSaleCustom, self).shop(page, category, search, min_price, max_price, ppg, **post)
		# theme_id = request.website.sudo().theme_id
		# if theme_id and theme_id.name.startswith('website_universal'):
		# brands = request.env['product.brand'].search(request.website.website_domain())
		# prices = request.env['product.template'].read_group(request.website.website_domain(), ['max_price:max(list_price)', 'min_price:min(list_price)'], [])[0]
		# min_price = float(prices['min_price'] or 0)
		# max_price = float(prices['max_price'] or 0)
		# keep = QueryURL(
		# 	'/shop',
		# 	category=category and int(category),
		# 	search=search,
		# 	attrib=request.httprequest.args.getlist('attrib'),
		# 	ppg=ppg,
		# 	order=post.get('order'),
		# 	min_price=request.httprequest.args.get('min_price'),
		# 	max_price=request.httprequest.args.get('max_price'),
		# 	brand=request.httprequest.args.getlist('brand'),
		# )

		# Grid Sizing
		bins = []
		for product in response.qcontext.get('products'):
			bins.append([{
				'ribbon': product.website_ribbon_id,
				'product': product,
				'x': 2,
				'y': 3
			}])

		attrib_list = request.httprequest.args.getlist('attrib')
		attrib_values = [[int(x) for x in v.split('-')] for v in attrib_list if v]
		# attributes_ids = [v[0] for v in attrib_values]  # Custom created
		Product = request.env['product.template'].with_context(bin_size=True)
		domain = self._get_search_domain(search, None, attrib_values)
		search_product = Product.search(domain)
		get_category_count = request.env['product.template']._get_product_category_count(website_ids=request.website.ids, product_ids=search_product.ids)
		response.qcontext.update(
			get_category_count=get_category_count,
			bins=bins,
		)
		# # Attributes
		# Product = request.env['product.template'].with_context(bin_size=True)
		# domain = self._get_search_domain(search, category, [])
		# search_product = Product.search(domain)
		# get_attrib_count = request.env['product.template']._get_product_attrib_count(website_ids=request.website.ids, product_ids=search_product.ids, attrib_values=attrib_values)
		# response.qcontext.update(
		# 	get_attrib_count=get_attrib_count,
		# )
		# # Brand
		# domain = self._get_search_domain(search, category, attrib_values)
		# brand_counts = request.env['product.template'].read_group(domain, ['brand_id'], 'brand_id')
		# response.qcontext.update(
		# 	get_brands_count=dict([(x['brand_id'][0], x['brand_id_count']) for x in brand_counts if x['brand_id']]),
		# )
		# response.qcontext.update(
		# 	brands=brands,
		# 	keep=keep,
		# 	min_price=min_price,
		# 	max_price=max_price,
		# 	bins=bins,
		# 	attributes_ids=attributes_ids,
		# 	selected_brands=[int(x) for x in request.httprequest.args.getlist('brand')],
		# )
		# # return request.render('website_universal.universal_products', response.qcontext)
		return response

	@http.route('/website_universal/get_quick_view_html', type='json', auth='public', website=True)
	def get_quick_view_html(self, options, **kwargs):
		productID = options.get('productID')
		variantID = options.get('variantID')
		product = False
		if variantID:
			productID = request.env['product.product'].browse(variantID).product_tmpl_id.id

		domain = expression.AND([request.website.website_domain(), [('id', '=', productID)]])
		product = request.env['product.template'].search(domain, limit=1)
		if not product:
			return []
		is_single_product = options.get('add_if_single_variant') and product.product_variant_count == 1

		values = self._prepare_product_values(product, category='', search='', **kwargs)
		Website = request.website
		view_track = request.website.viewref("website_universal.universal_product_quick_view").track
		values['view_track'] = view_track
		return request.env["ir.ui.view"]._render_template('website_universal.universal_product_quick_view', values=values)

	@http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
	def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
		res = super(WebsiteSaleCustom, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)
		# theme_id = request.website.sudo().theme_id
		# if theme_id and theme_id.name.startswith('theme_universal'):
		order = request.website.sale_get_order()
		FieldMonetary = request.env['ir.qweb.field.monetary']
		res['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
			"website_sale.cart_lines", {
				'website_sale_order': order,
				'date': fields.Date.today(),
				'suggested_products': order._cart_accessories()
			}
		)
		res['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template(
			"website_sale.short_cart_summary", {
				'website_sale_order': order,
			}
		)
		monetary_options = {
			'display_currency': request.website.get_current_pricelist().currency_id,
		}
		res['amount_total'] = FieldMonetary.value_to_html(order.amount_total, monetary_options)
		return res

	@http.route('/fetch/products_items', type='http', auth="public", methods=['POST'], website=True, csrf=False)
	def fetching_products(self, **kwargs):
		domains = [request.website.sale_product_domain(), [('website_published', '=', True)]]
		domain = []
		if kwargs.get('domain'):
			domain = json.loads(kwargs.get('domain'))
			domains.append(expression.AND(domain))
		products = request.env['product.template'].search(domain)
		is_recently = False
		if kwargs.get('is_recently'):
			is_recently = True
		if is_recently:
			products = False
			visitor = request.env['website.visitor']._get_visitor_from_request()
			excluded_products = request.website.sale_get_order().mapped('order_line.product_id.id')
			products = request.env['website.track'].sudo().read_group(
				[('visitor_id', '=', visitor.id), ('product_id', '!=', False), ('product_id.website_published', '=', True), ('product_id', 'not in', excluded_products)],
				['product_id', 'visit_datetime:max'], ['product_id'], limit=12, orderby='visit_datetime DESC')
			products_ids = [product['product_id'][0] for product in products]
			if products_ids:
				viewed_products = request.env['product.product'].with_context(display_default_code=False).browse(products_ids)
				products = viewed_products.mapped('product_tmpl_id')
		pricelist = request.website.get_current_pricelist()
		website = request.website
		res = request.env["ir.ui.view"]._render_template('website_universal.owl_carousel_item', values={
				'pricelist': pricelist,
				'products': products,
				'add_qty': 1,
				'website': website
			})
		if res:
			return res
		return ''