from odoo import api, fields, models, _


class UomUom(models.Model):
	_inherit = 'uom.uom'

	def set_uom_to_odoo(self, uom_ids, store):
		uom_category = self.env['uom.category']
		mapped_dict = dict()
		records = store.established_connection('uom.uom', 'search_read', [['id', 'in', uom_ids], ['active', 'in', [True, False]]], {'order':'id Asc'})
		for rec in records:
			category = uom_category.search([('name', 'ilike', rec.get('category_id')[1])])
			if not category:
				category = uom_category.create({'name': rec.get('category_id')[1]})

			uom_type = rec.get('uom_type')
			if uom_type == 'reference':
				reference_uom = self.search([('category_id', '=', category.id), ('uom_type', '=', 'reference')])
				if reference_uom:
					uom_type = 'bigger'
			
			vals = {'name': rec.get('name'),
			'uom_type': uom_type,
			'factor': rec.get('factor'),
			'factor_inv': rec.get('factor_inv'),
			'active': rec.get('active'),
			'rounding': rec.get('rounding'),
			'category_id': category.id
			}

			uom = self.search([('name', 'ilike', rec.get('name')), ('uom_type', '=', uom_type),('active', 'in', [True, False])], limit=1)
			if not uom:	
				uom = self.create(vals)
			else:
				uom.write(vals)
			mapped_dict[rec.get('id')] = uom.id
		return mapped_dict
