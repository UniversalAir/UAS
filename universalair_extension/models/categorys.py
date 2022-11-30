from odoo import api, fields, models, tools, _
from odoo.tools.translate import html_translate

class ProductPublicCategory(models.Model):
	_inherit = "product.public.category"

	is_display_header = fields.Boolean(string="Is Display Header")
	is_branded = fields.Boolean(string="Is Branded category")