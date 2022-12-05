from odoo import api, fields, models

class Rescompany(models.Model):
	_inherit = 'res.company'

	other_phone = fields.Char(related='partner_id.other_phone', store=True, readonly=False)
	fax = fields.Char(related='partner_id.fax', store=True, readonly=False)