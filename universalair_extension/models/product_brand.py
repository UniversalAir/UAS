# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReimoProductBrand(models.Model):
	_name = 'product.brand'
	_inherit = ['website.multi.mixin']
	_description = 'Product Brand'
	_order = 'sequence,id'

	name = fields.Char(required=True, translate=True)
	description = fields.Char(translate=True)
	image = fields.Binary()
	product_ids = fields.One2many('product.template', 'brand_id')
	# product_count = fields.Integer(compute='_compute_product_count')
	sequence = fields.Integer(string='Sequence')
	active = fields.Boolean(default=True)