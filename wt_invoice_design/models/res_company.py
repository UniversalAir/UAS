from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    account_number = fields.Integer(string="Account Number")