# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.addons.website.models import ir_http
from odoo.http import request

class Website(models.Model):
	_inherit = 'website'

	def get_all_parent_categories(self):
		cate_ids = self.env['product.public.category'].search([('parent_id', '=', False)])
		return cate_ids
		
	def get_header_display_categories(self):
		cate_ids = self.env['product.public.category'].search([('is_display_header', '=', True)])
		return cate_ids

	def get_branded_categories(self):
		cate_ids = self.env['product.public.category'].search([('is_branded', '=', True)])
		return cate_ids

	def get_other_pricelist(self):
		pricelist = request.website.get_current_pricelist()
		pricelists_ids = self.get_pricelist_available()
		other = pricelists_ids.filtered(lambda x: x.id != pricelist.id and x.is_wholesale_pricelist == False)
		if len(other) > 1:
			return other[0]
		return other 

	@api.model
	def get_category_breadcum(self, category):
		data = []
		parent_categ = False
		if category:
			categ_data = self.env['product.public.category'].search([('id', '=', int(category))])
			data.append(categ_data)
			parent_categ = categ_data
			if categ_data and categ_data.parent_id:
				parent_categ = categ_data.parent_id
				data.append(parent_categ)
				while parent_categ.parent_id:
					parent_categ = parent_categ.parent_id
					data.append(parent_categ)
			data.reverse()
		return data

	def sale_get_order(self, force_create=False, update_pricelist=False):
		sale_order = super(Website, self).sale_get_order(force_create, update_pricelist)
		if sale_order and sale_order.state == 'draft':
			if request.session.get('website_sale_current_pl'):
				sale_order.write({'pricelist_id': request.session.get('website_sale_current_pl')})
				sale_order.action_update_prices()

		if sale_order and sale_order.pricelist_id:
			category_dict ={}
			for line in sale_order.order_line:
				if line.product_id.categ_id.id in category_dict:
					category_dict[line.product_id.categ_id.id] += line.product_uom_qty
				else:
					category_dict[line.product_id.categ_id.id] = line.product_uom_qty

			for line in sale_order.order_line:
				if line.product_id.categ_id.id in category_dict:
					quantity = category_dict.get(line.product_id.categ_id.id)

					product_context={
						'partner': sale_order.partner_id,
						'quantity': quantity,
						'date': sale_order.date_order,
						'pricelist': sale_order.pricelist_id.id,
					}
					product = self.env['product.product'].with_context(product_context).with_company(sale_order.company_id.id).browse(line.product_id.id)
					line.price_unit = float(product.lst_price)
		return sale_order