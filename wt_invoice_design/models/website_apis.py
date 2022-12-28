from odoo import models, fields

class WebApi(models.Model):
	_inherit = "res.company"

	server_url = fields.Char(string="Enter Url")
	x_api_key = fields.Char(string="X-Api-Key")


class WebData(models.Model):
	_name = "web.data"

	website_code = fields.Char(string="Website Code")
	user_id = fields.Char(string="User Id")
	plateform_type = fields.Char(string="Plateform Type")
	data_source = fields.Char(string="Data Source")
	url = fields.Char(string="Url")
	response = fields.Char(string="Response")