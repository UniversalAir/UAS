# -*- coding: utf-8 -*-
from odoo import fields, models
from html.parser import HTMLParser
import xmlrpc.client
import datetime
from dateutil.relativedelta import relativedelta


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class ProductImage(models.Model):
    _inherit = 'product.image'

    db_id = fields.Integer()
    store_id = fields.Many2one('product.sync')

    def set_images_to_odoo(self, image_ids, store):
        product_image = self.env['product.image']
        records = store.established_connection('product.image', 'search_read', [["id", "in", image_ids]], False)

        for rec in records:
            vals = {'image_1920': rec.get('image_1920'),
            'name': rec.get('name'),
            'db_id': rec.get('id'),
            'store_id': store.id}
            img = product_image.search([('db_id', '=', rec.get('id')), ('store_id', '=', store.id)])
            if not img:
                img = product_image.create(vals)
            else:
                img.write(vals)

class ProductSync(models.Model):
    _name = "product.sync"
    _description = "Db Instance"
    _rec_name = 'name'

    name = fields.Char(string="Store Name", required=True, help="Store Name you would like to have")
    url = fields.Char(string="Url", help="url of database you want to fetch data http://warlocktechnologies.com", required=True,)
    database = fields.Char(string="Database", help="database name of the target url", required=True,)
    username = fields.Char(string="User Name", help="admin user name of target url", required=True,)
    password = fields.Char(string="Password", help="password of user name of target url", required=True,)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
    is_public_categ_done = fields.Boolean(default=False)
    # company_id = fields.Many2one('res.company', domain="[('db_id', '!=', False)]")
    last_synced_product_id = fields.Integer(default=0)
    company_id = fields.Many2one('res.company')
    last_product_tmpl_import_history = fields.Datetime()
    last_bom_import_history = fields.Datetime()

    count = fields.Integer(default=0)
    bom_count = fields.Integer(default=0)

    def display_message(self, message):
        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": message
                },
            }
        else:
            return True

    def cron_sync_products(self):
        for instance in self.search([]):
            queues = self.env['product.queue'].search([('state', 'not in', ['done']), ('instance_id', '=', instance.id)])
            for queue in queues:
                instance.with_context({'manual': True}).set_products_to_odoo(queue.product_data_queue_lines)
    
    def convert_html_to_text(self, data):
        converted_text = ""
        if data:
            f = HTMLFilter()
            f.feed(data)
            converted_text += f.text or ""
        return converted_text

    # Product Category
    def get_product_category(self, category):
        category = category[1].split("/")
        categ_id = False
        parent_id = False
        product_category_obj = self.env["product.category"]
        for catg_len in range(len(category)):
            categ_id = product_category_obj.search(
                [("name", "=", category[catg_len].strip())], limit=1
            )
            if not categ_id:
                categ_id = product_category_obj.create(
                    {"name": category[catg_len].strip()}
                )
            is_categ = product_category_obj.search(
                [("id", "=", parent_id)], limit=1
            )
            if is_categ:
                categ_id.parent_id = is_categ.id
            parent_id = categ_id.id
        return categ_id


    # product attributes for varient
    def sync_product_attributes(self, attribute_line, product_id):
        Attribute = self.env["product.attribute"]
        AttributeValue = self.env["product.attribute.value"]
        AttributeLine = self.env["product.template.attribute.line"]

        line_records = self.established_connection('product.template.attribute.line', 'search_read', [["id", "in", attribute_line]], False)
        done_attribute = []
        values = dict() 
        for line_rec in line_records:
            if line_rec.get('attribute_id')[0] not in values:
                values[line_rec.get('attribute_id')[0]] = {'name': line_rec.get('attribute_id')[1], 'attr_value': line_rec.get('value_ids')}
            else:
                values[line_rec.get('attribute_id')[0]]['attr_value'] = list(set(values[line_rec.get('attribute_id')[0]]['attr_value'] + line_rec.get('value_ids')))
        
        value_dict = dict()
        for attr in values:
            self_attribute = Attribute.search(
                [("name", "=", values.get(attr).get('name'))]
            )
            if not self_attribute:
                self_attribute = Attribute.create(
                    {"name": values.get(attr).get('name')}
                )

            db_att_value = self.established_connection('product.attribute.value', 'search_read', [["id", "in", values.get(attr).get('attr_value')]], False)
            for value in db_att_value:
                self_att_value = AttributeValue.search([("name", "=", value.get("name")),("attribute_id", "=", self_attribute.id)])
                if not self_att_value:
                    self_att_value = AttributeValue.create(
                        {
                            "name": value.get("name"),
                            "attribute_id": self_attribute.id,
                        }
                    )
                value_dict[value.get('id')] = self_att_value.id
        
        attr_line = AttributeLine.search([('product_tmpl_id', '=', product_id.id)])
        for line_rec in line_records:
            self_attribute = Attribute.search(
                [("name", "=", line_rec.get('attribute_id')[1])]
            )
            db_att_value_ids = [value_dict.get(key) for key in line_rec.get('value_ids')]
            attr_line_values = attr_line.filtered(lambda x: sorted(x.value_ids.ids) == sorted(db_att_value_ids))
            if not attr_line_values:
                AttributeLine.sudo().create(
                    {
                        "product_tmpl_id": product_id.id,
                        "attribute_id": self_attribute.id,
                        "value_ids": [(6, 0, db_att_value_ids)],
                    }
                )
            else:
                attr_line_values.write(
                    {
                        "product_tmpl_id": product_id.id,
                        "attribute_id": self_attribute.id,
                        "value_ids": [(6, 0, db_att_value_ids)],
                    }
                )

    
    # get seller ids
    def get_varient_seller_ids(self, db_product, tmpl_prdt):
        Partner = self.env["res.partner"]
        SupplierInfo = self.env["product.supplierinfo"]
        ProductProduct = self.env['product.product']

        seller_ids = self.established_connection('product.supplierinfo', 'search_read', [["id", "in", db_product.get("seller_ids")]], False) 

        for db_seller_id in seller_ids:
            name = db_seller_id.get("name")
            partner = False
            if name:
                partner = self.find_partner(name[1])
            
            vals = {"name": partner.id,
            "product_name": db_seller_id.get("product_name"),
            "product_code": db_seller_id.get("product_code"),
            "min_qty": db_seller_id.get("min_qty"),
            "price": db_seller_id.get("price"),
            "product_tmpl_id": tmpl_prdt.id,
            "company_id": self.company_id.id,
            "db_id": db_seller_id.get('id'),
            "instance_id": self.id
            }

            if db_seller_id.get('product_id'):
                prdt_prdt = self.established_connection('product.product', 'search_read', [['id', '=', db_seller_id.get('product_id')[0]], ['active', 'in', [True, False]]])
                prdt_tmpl = self.established_connection('product.product', 'search_read', [['id', 'in', prdt_prdt.get('product_tmpl_id')[0]], ['active', 'in', [True, False]]])

                prdt = self.find_product(prdt_prdt, prdt_tmpl)
                vals['product_id'] = prdt.id     

            supplier = SupplierInfo.sudo().search([('db_id', '=', db_seller_id.get('id')), ('instance_id', '=', self.id), ('company_id', '=', self.company_id.id)])
            if not supplier:
                supplier = SupplierInfo.sudo().create(vals)
            else:
                supplier.write(vals)

        
    def sync_product_varient_update(self, db_product, product_tmpl_id):
        product_product_obj = self.env["product.product"]
        # AttributeValue = self.env["product.template.attribute.value"]

        # product_product = self.env['product.product']
        product_template = self.env['product.template']

        product_template_attribute_value = self.env['product.template.attribute.value']
        product_attribute_value = self.env['product.attribute.value']
        product_attribute = self.env['product.attribute']
        Quant = self.env["stock.quant"]

        # get default warehouse
        # warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.company_id.id)], limit=1)
        db_product_varients = self.established_connection('product.product', 'search_read', [["product_tmpl_id", "=", db_product.get('id')], ['active', 'in', [True, False]]], False)
        varients = product_product_obj.sudo().search([("product_tmpl_id", "=",product_tmpl_id.id)])

        tmpl_attribute_value_ids = []
        for varient_rec in db_product_varients:
            if varient_rec.get('product_template_attribute_value_ids'):
                tmpl_attribute_value_ids += varient_rec.get('product_template_attribute_value_ids')

        mapped_tmpl_attribute_value_ids = {}
        if tmpl_attribute_value_ids:
            records = self.action_product_template_attribute_value_sync(list(set(tmpl_attribute_value_ids)))
            for rec in records:
                attr = product_attribute.search([('name', '=', rec.get('attribute_id')[1])])
                attr_val = product_attribute_value.search([('attribute_id', '=', attr.id), ('name', '=', rec.get('name'))])
                tmpl = product_template.search([('db_id', '=', rec.get('product_tmpl_id')[0]), ('store_id', '=', self.id), ('active', 'in', [True, False])])
                tmpl_attr_val = product_template_attribute_value.search([('product_tmpl_id', '=', tmpl.id), ('product_attribute_value_id', '=', attr_val.id), ('attribute_id', '=', attr.id)])
                mapped_tmpl_attribute_value_ids[rec.get('id')] = tmpl_attr_val.id

        for varient_rec in db_product_varients:
            varients = product_product_obj.sudo().search([("product_tmpl_id", "=",product_tmpl_id.id)])
            update_varients = varients.filtered(lambda x: x.partner_ref == varient_rec.get("display_name"))
            if not update_varients:
                try:
                    varient_ref = varient_rec.get("display_name").split("] ")[1]
                except:
                    varient_ref = varient_rec.get("display_name")
                update_varients = varients.filtered(lambda x: x.partner_ref == varient_ref and x.product_tmpl_id.id == product_tmpl_id.id)

            if not update_varients:
                prdt_tmpl_attr_val_ids = list(map(lambda x: mapped_tmpl_attribute_value_ids.get(x), varient_rec.get('product_template_attribute_value_ids')))
                update_varients = varients.filtered(lambda x: sorted(x.product_template_attribute_value_ids.ids) == sorted(prdt_tmpl_attr_val_ids))


            vals = {
                    "name": varient_rec.get("name"),
                    "type": varient_rec.get("type"),
                    # "price": varient_rec.get("price"),
                    "lst_price": varient_rec.get("lst_price"),
                    "standard_price": varient_rec.get("standard_price"),
                    "default_code": varient_rec.get("default_code"),
                    "code": varient_rec.get("code"),
                    "standard_price": varient_rec.get("standard_price"),
                    "volume": varient_rec.get("volume"),
                    "weight": varient_rec.get("weight"),
                    "description": varient_rec.get("description", ""),
                    "volume_uom_name": varient_rec.get("volume_uom_name"),
                    "weight_uom_name": varient_rec.get("weight_uom_name"),
                    "image_variant_1920": varient_rec.get("image_variant_1920"),
                    "description_sale": db_product.get("description_sale", ""),
                    "description_purchase": db_product.get("description_purchase"),
                    "description_pickingin": db_product.get("description_pickingin"),
                    "description_pickingout": db_product.get("description_pickingout"),
                    "db_id" : varient_rec.get("id"),
                    "store_id": self.id
                }

            barcode = varient_rec.get("barcode")
            if barcode:
                prdt = self.env['product.product'].sudo().search([('barcode', '=', varient_rec.get("barcode"))])
                if prdt:
                    prdt.barcode = ''
                vals['barcode'] = barcode

            update_varients.write(vals)

            for att_value in varient_rec.get("product_template_attribute_value_ids"):
                prdt_tmpl_attr_val = product_template_attribute_value.browse(mapped_tmpl_attribute_value_ids.get(att_value))
                db_prdt_tmpl_attr_val = list(filter(lambda x: x.get('id') == att_value, records))
                if db_prdt_tmpl_attr_val and prdt_tmpl_attr_val:
                    prdt_tmpl_attr_val.price_extra = db_prdt_tmpl_attr_val[0].get("price_extra")


            # qty according to varient
            # if (
            #     varient_rec.get("qty_available")
            #     and update_varients
            #     and update_varients.type == "product"
            # ):
            #     Quant.with_context(
            #         inventory_mode=True
            #     ).create(
            #         {
            #             "product_id": update_varients.id,
            #             "location_id": warehouse.lot_stock_id.id,
            #             "inventory_quantity": varient_rec.get("qty_available"),
            #         }
            #     )

    def action_category_sync(self):
        count = self.count
        while True:
            categories = self.established_connection('product.public.category', 'search_read', [['id', '>', count]], {'limit': 100, 'order':'id Asc'})
            if categories:
                self.set_categories_to_odoo(categories)
                count = int(categories[-1]['id'])
            else:
                self.is_public_categ_done = True
                break

    def set_categories_to_odoo(self, category_ids):
        product_public_category = self.env['product.public.category']
        categories = self.established_connection('product.public.category', 'search_read', [['id', 'in', category_ids]], {'order':'id Asc'})
        mapped_dict = {}
        for rec in categories:
            parent_id = False
            if rec.get('parent_id'):
                for name in rec.get('parent_id')[1].split('/'):
                    parent_categ = product_public_category.search([('name', '=', name), ('parent_id', '=', parent_id)])
                    if not parent_categ:
                        parent_categ = product_public_category.create({'name': name, 'parent_id': parent_id})
                    parent_id = parent_categ.id
            category = product_public_category.search([('name', '=', rec.get('name')), ('parent_id', '=', parent_id)])
            if not category:
                category = product_public_category.create({'name': rec.get('name'), 'parent_id': parent_id})
            mapped_dict[rec.get('id')] = category.id
        return mapped_dict

    def action_bom_sync(self):
        mrp_bom = self.env['mrp.bom']
        count = self.bom_count
        write_date = self.last_bom_import_history
        if not self.last_bom_import_history:
            write_date = str((datetime.datetime.now() - relativedelta(years=1000)).date())
        while True:
            boms = self.established_connection('mrp.bom', 'search_read', [['id', '>', count], ['active', 'in', [True, False]]], {'limit': 100, 'order':'id'})
            if boms:
                mrp_bom.set_bom_to_odoo(boms, self)
                count = int(boms[-1]['id'])
                self._cr.commit()
            else:
                self.bom_count = 0
                break

    def action_product_template_attribute_value_sync(self, ids):
        records = self.established_connection('product.template.attribute.value', 'search_read', [['id', 'in', ids]], {'order':'id'})
        return records


    def action_bom_line_sync(self, line_ids):
        mrp_bom = self.env['mrp.bom']
        count = self.bom_count
        # while True:
        bom_lines = self.established_connection('mrp.bom.line', 'search_read', [['id', 'in', line_ids]], {'order':'id'})
        return bom_lines
            # products = self.established_connection('product.template', 'search_read', [['id', '=', 35], ['active', 'in', [True, False]]], {'limit': 100, 'order':'id'})


    def action_product_sync(self):
        count = self.count
        write_date = self.last_product_tmpl_import_history
        if not self.last_product_tmpl_import_history:
            write_date = str((datetime.datetime.now() - relativedelta(years=1000)).date())
        while True:
            products = self.established_connection('product.template', 'search_read', [['write_date', '>', write_date], ['id', '>', count], ['active', 'in', [True, False]]], {'limit': 100, 'order':'id'})
            # products = self.established_connection('product.template', 'search_read', [['id', '=', 35], ['active', 'in', [True, False]]], {'limit': 100, 'order':'id'})
            if products:
                self.set_products_to_odoo(products)
                count = int(products[-1]['id'])
                self._cr.commit()
            else:
                last_updated_product = self.established_connection('product.template', 'search_read', [['active', 'in', [True, False]]], {'fields':['write_date'], 'limit': 1, 'order':'write_date desc'})
                if last_updated_product:
                    self.last_product_tmpl_import_history = last_updated_product[0].get('write_date')
                self.count = 0
                break

    def set_products_to_odoo(self, products):
        product_obj = self.env["product.template"]
        Product = self.env['product.product']
        Quant = self.env["stock.quant"]
        AccountTax = self.env["account.tax"]
        ProductImage = self.env["product.image"]
        UomUom = self.env['uom.uom']
        UomCategory = self.env['uom.category']

        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.company_id.id)], limit=1)
        counter = 0
        user_ids = []
        tax_ids = []
        supplier_taxes_id = []
        tmpl_images = []
        uom_ids = []
        uom_po_ids = []
        public_categories = []

        for product in products:
            if product.get('taxes_id'):
                tax_ids = tax_ids + product.get('taxes_id')

            if product.get('supplier_taxes_id'):
                supplier_taxes_id += product.get('supplier_taxes_id')

            if product.get('product_template_image_ids'):
                tmpl_images += product.get('product_template_image_ids')

            if product.get('uom_id'):
                uom_ids += [product.get('uom_id')[0]]

            if product.get('uom_po_id'):
                uom_po_ids += [product.get('uom_po_id')[0]]

            if product.get('public_categ_ids'):
                public_categories += product.get('public_categ_ids')

        if tax_ids:
            AccountTax.set_taxes_to_odoo(list(set(tax_ids)), self)
        if supplier_taxes_id:
            AccountTax.set_taxes_to_odoo(list(set(supplier_taxes_id)), self)
        if tmpl_images:
            ProductImage.set_images_to_odoo(list(set(tmpl_images)), self)

        mapped_public_categories = {}   
        if public_categories:
            mapped_public_categories = self.set_categories_to_odoo(list(set(public_categories)))
        
        mapped_uom_ids = {}
        if uom_ids:
            mapped_uom_ids = UomUom.set_uom_to_odoo(list(set(uom_ids)), self)
        
        mapped_uom_po_ids = {}
        if uom_po_ids:
            mapped_uom_po_ids = UomUom.set_uom_to_odoo(list(set(uom_po_ids)), self)

        for product in products:
            print(">>>>>>>>>>>>>>>>>>>>%s>>>>>>>>>>>>>>>>>>>>>>>>%s"%(product.get('id'), product.get('active')))
            category_id = False
            if product.get("categ_id") and product["categ_id"][1]:
                category_id = self.get_product_category(product["categ_id"]).id

            taxes = []
            if product.get('taxes_id'):
                taxes = AccountTax.search([('db_id', 'in', product.get('taxes_id')), ('instance_id', '=', self.id)])

            supplier_taxes = []
            if product.get('supplier_taxes_id'):
                taxes = AccountTax.search([('db_id', 'in', product.get('supplier_taxes_id')), ('instance_id', '=', self.id)])

            uom_id = False
            if product.get('uom_id'):
                uom_id = mapped_uom_ids[product.get('uom_id')[0]]

            uom_po_id = False
            if product.get('uom_po_id'):
                uom_po_id = mapped_uom_po_ids[product.get('uom_po_id')[0]]

            public_categ_ids = []
            if product.get('public_categ_ids'):
                public_categ_ids = list(map(lambda x: mapped_public_categories.get(x), product.get('public_categ_ids')))


            if uom_id or uom_po_id:
                product_vals = {'uom_id': uom_id, 'uom_po_id': uom_po_id}

            product_vals.update({
                                "name": product.get("name"),
                                "type": product.get("type"),
                                "list_price": product.get("list_price"),
                                "default_code": product.get("default_code"),
                                "description": product.get("description", ""),
                                # "price": product.get("price"),
                                "standard_price": product.get("standard_price"),
                                "volume": product.get("volume"),
                                "volume_uom_name": product.get("volume_uom_name"),
                                "weight": product.get("weight"),
                                "website_description": product.get("website_description"),
                                "weight_uom_name": product.get("weight_uom_name"),
                                "uom_name": product.get("uom_name"),
                                "image_1920": product.get("image_1920"),
                                "is_published": product.get('is_published', False),
                                # "l10n_in_hsn_code": product.get("l10n_in_hsn_code"),
                                # "l10n_in_hsn_description": product.get("l10n_in_hsn_description"),
                                "description_sale": product.get('description_sale'),
                                "description_purchase": product.get("description_purchase"),
                                # "hs_code": product.get("hs_code"),
                                "description_pickingin": product.get("description_picking"),
                                "description_pickingout": product.get("description_pickingout"),
                                "categ_id": category_id,
                                'purchase_method': product.get('purchase_method'),
                                'website_sequence': product.get('website_sequence'),
                                "public_categ_ids": [(6, 0, public_categ_ids)] if public_categ_ids else [],
                                # "active": product.get("active"),
                                "invoice_policy": product.get("invoice_policy"),
                                "taxes_id": [(6, 0, taxes.ids)] if taxes else [],
                                "supplier_taxes_id": [(6, 0, supplier_taxes.ids)] if supplier_taxes else [], 
                                "db_id": product['id'],
                                "store_id": self.id,
                                # 'compatible_ids': [(6, 0, compatible_ids)] if compatible_ids else [],
                            })

            product_id = product_obj.sudo().search([('db_id', '=', product['id']), ('store_id', '=', self.id), ('active', 'in', [True, False])])
            if not product_id:
                product_id = product_obj.sudo().create(product_vals)
            else:
                product_id.write(product_vals)

            if product.get('product_template_image_ids'):
                images = ProductImage.search([('db_id', 'in', product.get('product_template_image_ids')), ('store_id','=', self.id)])
                images.product_tmpl_id = product_id.id
            # product_id.company_id = self.company_id.id

            ''' Product attribute remove if it's removed from v10 DB '''
            
            attribute_line = product.get("attribute_line_ids")


            # if not attribute_line:
            #     varient_id = Product.sudo().search(
            #         [("product_tmpl_id", "=", product_id.id)]
            #     )
            #     if (
            #         varient_id
            #         and varient_id.type == "product"
            #         and product.get("qty_available")
            #     ):
            #         Quant.with_context(
            #             inventory_mode=True
            #         ).create(
            #             {
            #                 "product_id": varient_id.id,
            #                 "location_id": warehouse.lot_stock_id.id,
            #                 "inventory_quantity": product.get("qty_available"),
            #             }
            #         )

            # get product attributes and values for varients
            if attribute_line:
                self.sync_product_attributes(attribute_line, product_id)

            self.sync_product_varient_update(product, product_id)
            get_seller_ids = []

            # if product.get("seller_ids"):
            #     self.get_varient_seller_ids(product, product_id)

            product_id.active = product.get("active")

            self.count = product.get('id')

            self._cr.commit()
            counter = counter + 1

    def product_sync_crons(self):
        store_obj = self.env['product.sync'].search([])
        for store in store_obj:
            store.action_product_sync()


    def established_connection(self, obj, event, domain, limit=False):
        url = self.url
        database = self.database
        username = self.username
        password = self.password
        url, db, username, password = url.strip(), database.strip(), username.strip(), password.strip()
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        vals = models.execute_kw(db, uid, password, obj, event, [domain], limit)
        return vals


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    db_id = fields.Integer(readonly=True)
    instance_id = fields.Many2one("product.sync", readonly=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    db_id = fields.Char(string="Product Store Id", readonly=True)
    store_id = fields.Many2one("product.sync", string="Store", readonly=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    db_id = fields.Integer(readonly=True)
    store_id = fields.Many2one('product.sync')
