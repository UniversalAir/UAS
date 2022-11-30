from odoo import api, fields, models

class ProductPricelist(models.Model):
	_inherit = 'product.pricelist'

	is_wholesale_pricelist = fields.Boolean(string="Is Wholesale Pricelist")