from odoo import api, fields, models

class ResPartner(models.Model):
	_inherit = 'res.partner'

	other_phone = fields.Char(string="Other Phone")
	fax = fields.Char(string="Fax")