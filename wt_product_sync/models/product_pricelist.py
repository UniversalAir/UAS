# -*- coding: utf-8 -*-
from odoo import fields, models
from html.parser import HTMLParser
import xmlrpc.client
from datetime import datetime


class ProductPrice(models.Model):
    _inherit = 'product.pricelist'

    db_id = fields.Integer()
    store_id = fields.Many2one('product.sync')


class ProducyPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    db_id = fields.Integer()
    store_id = fields.Many2one('product.sync')


class ResCountryGroup(models.Model):
    _inherit = 'res.country.group'

    db_id = fields.Integer()
    store_id = fields.Many2one('product.sync')


class Website(models.Model):
    _inherit = 'website'

    db_id = fields.Integer()
    store_id = fields.Many2one('product.sync')


class ProductSync(models.Model):
    _inherit = "product.sync"

    def action_product_pricelist_sync(self):
        count = 0            
        while True:
            pricelists = self.established_connection('product.pricelist', 'search_read', [['id', '>', count], ['active', 'in', [True, False]]], {'limit': 100, 'order':'id Asc'})
            if pricelists:
                self.set_products_pricelist_to_odoo(pricelists)
                count = int(pricelists[-1]['id'])
            else:
                break

    def sync_website(self, records):
        Website = self.env['website']
        ResCompany = self.env['res.company']
        ResLang = self.env['res.lang']
        IrModuleModule = self.env['ir.module.module']

        for rec in records:
            company = False
            if rec.get('company_id'):
                company = ResCompany.search([('db_id', '=', rec.get('company_id')[0])]).id
            lang = False
            if rec.get('default_lang_id'):
                lang = ResLang.search([('name', '=', rec.get('default_lang_id')[1]), ('active', 'in', [True, False])])
                lang.active = True
            module = False
            if rec.get('theme_id'):
                module = IrModuleModule.search([('name', '=', rec.get('theme_id')[1])])
            vals = {'name': rec.get('name'), 
            'domain': rec.get('domain'),
            'logo': rec.get('logo'),
            'company_id': company,
            'custom_code_head': rec.get('custom_code_head'),
            'theme_id': module.id if module else False,
            'default_lang_id': lang.id if lang else False}
            website = Website.search([('db_id', '=', rec.get('id')), ('store_id', '=', self.id)])
            if not website:
                website = Website.create(vals)
            else:
                website.write(vals)

    def sync_country_group(self, records):
        ResCountryGroup = self.env['res.country.group']
        ResCountry = self.env['res.country']
        for rec in records:
            lines = []
            if rec.get('country_ids'):
                countries = self.established_connection('res.country', 'search_read', [['id', 'in', rec.get('country_ids')]], {'order':'id Asc'})
                for country in countries:
                    country_obj = ResCountry.search([('name', '=', country.get('name')[1])])
                    lines.append(country_obj.id)
            vals = {'name': rec.get('name'),
            'country_ids': [(6, 0, lines)] if lines else [],
            'db_id': rec.get('id'),
            'store_id': self.id
            }
            grp = ResCountryGroup.search([('db_id', '=', rec.get('id')), ('store_id', '=', self.id)])
            if not grp:
                grp = ResCountryGroup.create(vals)
            else:
                grp.write(vals)

    def set_products_pricelist_to_odoo(self, pricelists):
        ProductPricelistItem = self.env['product.pricelist.item']
        ProductPricelist = self.env['product.pricelist']
        ProductTemplate = self.env['product.template']
        ProductProduct = self.env['product.product']
        ResCurrency = self.env['res.currency']
        ResCompany = self.env['res.company']
        ResCountryGroup = self.env['res.country.group']
        Website = self.env['website']

        country_groups = []
        website_ids = []
        for rec in pricelists:
            if rec.get('country_ids'):
                country_groups += rec.get('country_ids')
            if rec.get('website_id'):
                website_ids.append(rec.get('website_id')[0])
        country_groups = list(set(country_groups))
        website_ids = list(set(website_ids))
        
        country_groups = self.established_connection('res.country.group', 'search_read', [['id', 'in', country_groups]], {'order':'id Asc'})
        self.sync_country_group(country_groups)

        websites = self.established_connection('website', 'search_read', [['id', 'in', website_ids]], {'order':'id Asc'})
        self.sync_website(websites)

        for rec in pricelists:
            # import pdb;pdb.set_trace()
            print(">>>>>",rec.get('id'))
            pricelist = ProductPricelist.search([('db_id', '=', rec.get('id')), ('store_id', '=', self.id), ('active', 'in', [True, False])])         
            lines = []
            if rec.get('item_ids'):
                pricelist_items = self.established_connection('product.pricelist.item', 'search_read', [['id', 'in', rec.get('item_ids')], ['active', 'in', [True, False]]], {'order':'id Asc'})
                for item in pricelist_items:
                    date_start = False
                    if item.get('date_start'):
                        date_start = datetime.strptime(item.get('date_start'), '%Y-%m-%d %H:%M:%S')
                    date_end = False
                    if item.get('date_end'):
                        date_end = datetime.strptime(item.get('date_end'))
                    prdt_tmpl = False
                    if item.get('product_tmpl_id'):  
                        prdt_tmpl = ProductTemplate.search([('db_id', '=', item.get('product_tmpl_id')[0]), ('store_id', '=', self.id), ('active', 'in', [True, False])])
                    prdt_variant = False
                    if item.get('product_id'):
                        prdt_variant = ProductProduct.search([('db_id', '=', item.get('product_id')[0]), ('store_id', '=', self.id), ('active', 'in', [True, False])])
                    vals = {'product_tmpl_id': prdt_tmpl.id if prdt_tmpl else False,
                    'product_id': prdt_variant.id if prdt_variant else False,
                    'min_quantity': item.get('min_quantity'),
                    'fixed_price': item.get('fixed_price'),
                    'date_start': date_start,
                    'date_end': date_end,
                    'compute_price': item.get('compute_price'),
                    'applied_on': item.get('applied_on')
                    }
                    pricelist_item = ProductPricelistItem.search([('pricelist_id', '=', pricelist.id), ('db_id', '=', item.get('id')), ('active', 'in', [True, False])])
                    if pricelist_item:
                        lines.append((1, pricelist_item.id, vals))
                    else:
                        lines.append((0, 0, vals))
            # import pdb;pdb.set_trace()


            currecy = ResCurrency.search([('name', '=', rec.get('currency_id')[1]), ('active', 'in', [True, False])])
            currecy.active = True

            company = False
            if rec.get('company_id'):
                company = ResCompany.search([('db_id', '=', rec.get('company_id')[0])]).id

            website = False
            if rec.get('website_id'):
                website = Website.search([('db_id', '=', rec.get('website_id')[0]), ('store_id', '=', self.id)])

            country_ids = ResCountryGroup.search([('db_id', 'in', rec.get('country_group_ids'))])
            vals = {'name': rec.get('name'),
            'currency_id': currecy.id,
            'company_id': company,
            'selectable': rec.get('selectable'),
            'discount_policy': rec.get('discount_policy'),
            'website_id': website.id if website else False,
            'item_ids': lines,
            'country_group_ids': [(6, 0, country_ids.ids)] if country_ids else [],
            'db_id': rec.get('id'),
            'store_id': self.id}

            if not pricelist:
                pricelist = ProductPricelist.create(vals)
            else:
                pricelist.write(vals)

            print(">>>>>>>>>",pricelist)
