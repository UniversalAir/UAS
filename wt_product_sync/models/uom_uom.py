from odoo import api, fields, models, _


class UomUom(models.Model):
	_inherit = 'uom.uom'

	def set_uom_to_odoo(self, uom_ids, store):
		uom_category = self.env['uom.category']
		mapped_dict = dict()
		records = store.established_connection('uom.uom', 'search_read', [['id', 'in', uom_ids]], {'order':'id Asc'})
		for rec in records:
			category = uom_category.search([('name', 'ilike', rec.get('category_id')[1])])
			if not category:
				category = uom_category.create({'name': rec.get('category_id')[1]})

			uom = self.search([('name', 'ilike', rec.get('name')), ('uom_type', '=', rec.get('uom_type')),('active', '=', rec.get('active')), ('rounding', '=', rec.get('rounding'))])

			vals = {'name': rec.get('name'),
			'uom_type':rec.get('uom_type'),
			'ratio': rec.get('ratio'),
			'active': rec.get('active'),
			'rounding': rec.get('rounding'),
			'category_id': category.id
			}

			if not uom:
				uom = self.create(vals)
			else:
				uom.write(vals)
			mapped_dict[rec.get('id')] = uom.id
		return mapped_dict
