from odoo import http
from odoo.http import request
import werkzeug


class FoodDetails(http.Controller):

	@http.route('/fetch/products_items', type='http', auth="public", methods=['POST'], website=True, csrf=False)
	def fetching_products(self, **kwargs):
		# import pdb;pdb.set_trace()
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
		res = request.env["ir.ui.view"]._render_template('web_home_page.owl_carousel_item', values={
				'pricelist': pricelist,
				'products': products,
				'add_qty': 1,
				'website': website
			})
		if res:
			# import pdb;pdb.set_trace()
			return res
		return ''