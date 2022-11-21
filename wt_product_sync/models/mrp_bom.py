from odoo import api, fields, models, _

class MrpBOMLine(models.Model):
    _inherit = 'mrp.bom.line'

    db_id = fields.Integer()
    instance_id = fields.Many2one('product.sync')


class MrpBOM(models.Model):
    _inherit = 'mrp.bom'

    db_id = fields.Integer()
    instance_id = fields.Many2one('product.sync')

    def set_bom_to_odoo(self, records, store):
        mrp_bom_line = self.env['mrp.bom.line']
        product_product = self.env['product.product']
        product_template = self.env['product.template']
        product_template_attribute_value = self.env['product.template.attribute.value']
        product_attribute_value = self.env['product.attribute.value']
        product_attribute = self.env['product.attribute']
        UomUom = self.env['uom.uom']

        for rec in records:
            bom_lines = store.action_bom_line_sync(rec.get('bom_line_ids'))
            uom_ids = list(map(lambda x: x.get('product_uom_id')[0], bom_lines))

            tmpl_attribute_value_ids = []
            for line in bom_lines:
                if line.get('bom_product_template_attribute_value_ids'):
                    tmpl_attribute_value_ids.append(line.get('bom_product_template_attribute_value_ids')[1])

            mapped_uom_ids = {}
            if uom_ids:
                mapped_uom_ids = UomUom.set_uom_to_odoo(list(set(uom_ids)), store)

            mapped_tmpl_attribute_value_ids = {}
            if tmpl_attribute_value_ids:
                recs = store.action_product_template_attribute_value_sync(list(set(tmpl_attribute_value_ids)))
                for r in recs:
                    attr = product_attribute.search([('name', 'ilike', r.get('attribute_id')[1])])
                    attr_val = product_attribute_value.search([('attribute_id', '=', attr.id), ('name', 'ilike', r.get('product_attribute_value_id')[1])])
                    tmpl = product_template.search([('db_id', '=', r.get('product_tmpl_id')), ('store_id', '=', store.id), ('active', 'in', [True, False])])
                    tmpl_attr_val = product_template_attribute_value.search([('product_tmpl_id', '=', tmpl.id), ('product_attribute_value_id', '=', attr_val.id), ('attribute_id', '=', attr.id)])
                    mapped_tmpl_attribute_value_ids[r.get('id')] = tmpl_attr_val.id

            lines = []
            for line in bom_lines:
                vrnt = product_product.search([('db_id', '=', line.get('product_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
                uom_id = mapped_uom_ids.get(line.get('product_uom_id')[0], False)

                prdt_tmpl_attr_val_id = False
                if line.get('bom_product_template_attribute_value_ids'):
                    prdt_tmpl_attr_val_id = mapped_tmpl_attribute_value_ids[line.get('bom_product_template_attribute_value_ids')[0]]

                vals = {'product_id': vrnt.id, 
                'product_qty': line.get('product_qty'),
                'product_uom_id': uom_id,
                'bom_product_template_attribute_value_ids': prdt_tmpl_attr_val_id,
                'db_id': line.get('id'),
                'instance_id': store.id}

                bom_line = mrp_bom_line.search([('db_id', '=', line.get('id')), ('instance_id', '=', store.id)])
                if bom_line:
                    line.append((1, bom_line.id, vals))
                else:
                    line.append((0, 0, vals))

            prdt_tmpl = product_template.search([('db_id', '=', rec.get('product_tmpl_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
            vrnt = product_product.search([('db_id', '=', rec.get('product_id')), ('store_id', '=', store.id), ('active', 'in', [True, False])])
            vals = {'product_tmpl_id': prdt_tmpl.id, 
            'product_id': vrnt.id,
            'product_qty': rec.get('product_qty'),
            'code': rec.get('code'),
            'type': rec.get('type'),
            'consumption': rec.get('consumption'),
            'db_id': rec.get('id'),
            'instance_id': store.id}

            bom = self.search([('db_id', '=', rec.get('id')), ('instance_id', '=', store.id), ('active', 'in', [True, False])])
            if not bom:
                self.create(vals)
            else:
                bom.write(vals)

            store.count = rec.get('id')
            self._cr.commit()

