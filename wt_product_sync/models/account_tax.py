from odoo import api, fields, models, _


class AccountTax(models.Model):
	_inherit = 'account.tax'

	db_id = fields.Integer()
	instance_id = fields.Many2one('product.sync')


	def set_taxes_to_odoo(self, tax_ids, store):
		AccountTax = self.env['account.tax']
		AccountTaxRepartitionLine = self.env['account.tax.repartition.line']
		ResCountry = self.env['res.country']

		taxes = store.established_connection('account.tax', 'search_read', [['id', 'in', tax_ids]], {'order':'id Asc'})

		for tax in taxes:
			country = False
			if tax.get('country_id'):
				country = ResCountry.search([('name', '=', tax.get('country_id')[1])])

			vals = {'name': tax.get('name'),
			'amount_type': tax.get('amount_type'),
			'type_tax_use': tax.get('type_tax_use'),
			'tax_scope': tax.get('tax_scope'),
			'amount': tax.get('amount'),
			'country_id': country.id if country else False,
			'db_id': tax.get('id'),
			'country_id': self.env.company.country_id.id,
			'instance_id': store.id,
			# 'company_id': store.company_id.id
			}

			if tax.get('python_compute'):
				vals['python_compute'] = tax.get('python_compute')

			if tax.get('python_applicable'):
				vals['python_applicable'] = tax.get('python_applicable')

			account_tax = AccountTax.sudo().search([('db_id', '=', tax.get('id')),('instance_id', '=', store.id)])
			if not account_tax:
				account_tax = AccountTax.sudo().create(vals)
			else:
				account_tax.write(vals)

			child_tax = []
			if tax.get('children_tax_ids'):
				self.set_taxes_to_odoo(tax.get('children_tax_ids'), store)
				child_tax = AccountTax.sudo().search([('db_id', 'in', tax.get('children_tax_ids')), ('instance_id', '=', store.id)])
				for x in child_tax:
					x.type_tax_use = account_tax.type_tax_use
					x.tax_scope = account_tax.tax_scope
				account_tax.write({'children_tax_ids': [(6, 0, child_tax.ids)]})

			if tax.get('invoice_repartition_line_ids'):
				AccountTaxRepartitionLine.set_taxes_to_odoo(tax.get('invoice_repartition_line_ids'), 'invoice_tax_id', account_tax, store)
				
			if tax.get('refund_repartition_line_ids'):
				AccountTaxRepartitionLine.set_taxes_to_odoo(tax.get('refund_repartition_line_ids'), 'refund_tax_ids', account_tax, store)


class AccountTaxRepartitionLine(models.Model):
	_inherit = 'account.tax.repartition.line'

	db_id = fields.Integer()
	instance_id = fields.Many2one('product.sync')

	def set_taxes_to_odoo(self, line_ids, tax_type, account_tax, store):
		AccountAccount = self.env['account.account']

		distribution_line = store.established_connection('account.tax.repartition.line', 'search_read', [['id', 'in', line_ids]], {'limit': 100, 'order':'id Asc'})
		account_ids = []
		for x in distribution_line:
			if x.get('account_id'):
				account_ids.append(x.get('account_id')[0])

		if account_ids:
			mapped_acnt_dict = AccountAccount.set_accounts_to_odoo(account_ids, store)

		default_invoice_repartition = account_tax.invoice_repartition_line_ids.filtered(lambda x: x.db_id == False)
		if default_invoice_repartition:
			default_invoice_repartition.unlink()

		default_refund_repartiton = account_tax.refund_repartition_line_ids.filtered(lambda x: x.db_id == False)
		if default_refund_repartiton:
			default_refund_repartiton.unlink()	

		for line in distribution_line:
			account = False
			if line.get('account_id'):
				account = mapped_acnt_dict.get(line.get('account_id')[0])

			vals = {'factor_percent': line.get('factor_percent'),
			'repartition_type': line.get('repartition_type'),
			'account_id': account,
			'db_id': line.get('id'),
			'instance_id': store.id
			}
			if tax_type == 'refund_tax_ids':
				vals['refund_tax_id'] = account_tax.id
			else:
				vals['invoice_tax_id'] = account_tax.id
				
			tax = self.search([('db_id', '=', line.get('id')), ('instance_id', '=', store.id)])
			if not tax:
				self.create(vals)
			else:
				tax.write(vals)


class AccountAccount(models.Model):
	_inherit = "account.account"

	def set_accounts_to_odoo(self, account_ids, store):
		# AccountAccountType = self.env['account.account.type']
		charts_of_account = store.established_connection('account.account', 'search_read', [['id', 'in', account_ids]])
		AccountAccount = self.env['account.account']
		ResCompany = self.env['res.company']

		mapped_acnt_dict = {}
		for acnt in charts_of_account:
			# user_type_id = AccountAccountType.search([('name', '=', acnt.get('user_type_id')[1])])
			company = False
			# if acnt.get('company_id'):
			# 	company = ResCompany.sudo().search([('db_id', '=', acnt.get('company_id')[0])])
			vals = {'code': acnt.get('code'),
			'name': acnt.get('name'),
			# 'user_type_id': user_type_id.id,
			'reconcile': acnt.get('reconcile'),
			# 'company_id': company.id if company else False, 
			}

			# account = AccountAccount.sudo().search([('code', '=', acnt.get('code')), ('company_id', '=', company.id)])
			account = AccountAccount.sudo().search([('code', '=', acnt.get('code'))])
			
			if not account:
				account = AccountAccount.sudo().create(vals)
			else:
				account.write(vals)
			mapped_acnt_dict[acnt.get('id')] = account.id

		return mapped_acnt_dict


class AccountJournal(models.Model):
	_inherit = 'account.journal'


	def set_journals_to_odoo(self, journal_ids, store):
		AccountJournal = self.env['account.journal']
		AccountAccount = self.env['account.account']
		
		account_journals = store.established_connection('account.journal', 'search_read', [['id', 'in', journal_ids]])
		mapped_jrnl_dict = {}

		for journal in account_journals:
			account = AccountAccount.search([('name', '=', journal.get('default_account_id')[1])])
			vals = {'name': journal.get('name'), 
			'type': journal.get('type'),
			'code': journal.get('code'),
			'default_account_id': account.id,
			# 'company_id': store.company_id.id
			}

			# jrnl = AccountJournal.sudo().search([('code', '=', journal.get('code')), ('name', '=', journal.get('name')), ('company_id', '=', store.company_id.id)])
			jrnl = AccountJournal.sudo().search([('code', '=', journal.get('code')), ('name', '=', journal.get('name'))])			
			if not jrnl:
				jrnl = AccountJournal.sudo().create(vals)
			else:
				jrnl.write(vals)

			mapped_jrnl_dict[journal.get('id')] = jrnl.get('id')

		return mapped_jrnl_dict

