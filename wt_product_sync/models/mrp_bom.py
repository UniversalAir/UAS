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
                    tmpl_attribute_value_ids += line.get('bom_product_template_attribute_value_ids')

            mapped_uom_ids = {}
            if uom_ids:
                mapped_uom_ids = UomUom.set_uom_to_odoo(list(set(uom_ids)), store)

            mapped_tmpl_attribute_value_ids = {}
            if tmpl_attribute_value_ids:
                reccords = store.action_product_template_attribute_value_sync(list(set(tmpl_attribute_value_ids)))
                for recc in reccords:
                    if recc.get('ptav_active'):    
                        attr = product_attribute.search([('name', '=', recc.get('attribute_id')[1])])
                        attr_val = product_attribute_value.search([('attribute_id', '=', attr.id), ('name', '=', recc.get('name'))])
                        tmpl = product_template.search([('db_id', '=', recc.get('product_tmpl_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
                        tmpl_attr_val = product_template_attribute_value.search([('product_tmpl_id', '=', tmpl.id), ('product_attribute_value_id', '=', attr_val.id), ('attribute_id', '=', attr.id)])
                        mapped_tmpl_attribute_value_ids[recc.get('id')] = tmpl_attr_val.id

            lines = []

            for line in bom_lines:
                vrnt = product_product.search([('db_id', '=', line.get('product_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
                if not vrnt:
                    continue
                uom_id = mapped_uom_ids.get(line.get('product_uom_id')[0], False)

                prdt_tmpl_attr_val_ids = []
                if line.get('bom_product_template_attribute_value_ids'):
                    for x in line.get('bom_product_template_attribute_value_ids'):
                        if mapped_tmpl_attribute_value_ids.get(x):
                            prdt_tmpl_attr_val_ids.append(mapped_tmpl_attribute_value_ids.get(x))
                    # prdt_tmpl_attr_val_ids = list(map(lambda x: mapped_tmpl_attribute_value_ids.get(x), line.get('bom_product_template_attribute_value_ids')))
                
        
                vals = {'product_id': vrnt.id, 
                'product_qty': line.get('product_qty'),
                'product_uom_id': uom_id,
                'bom_product_template_attribute_value_ids': [(6, 0, prdt_tmpl_attr_val_ids)] if prdt_tmpl_attr_val_ids else [],
                'db_id': line.get('id'),
                'instance_id': store.id}

                bom_line = mrp_bom_line.search([('db_id', '=', line.get('id')), ('instance_id', '=', store.id)])
                if bom_line:
                    lines.append((1, bom_line.id, vals))
                else:
                    lines.append((0, 0, vals))

            prdt_tmpl = product_template.search([('db_id', '=', rec.get('product_tmpl_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
            vrnt = False
            if rec.get('product_id'):
                vrnt = product_product.search([('db_id', '=', rec.get('product_id')[0]), ('store_id', '=', store.id), ('active', 'in', [True, False])])
            vals = {'product_tmpl_id': prdt_tmpl.id, 
            'product_id': vrnt.id if vrnt else vrnt,
            'product_qty': rec.get('product_qty'),
            'code': rec.get('code'),
            'type': rec.get('type'),
            'bom_line_ids': lines,
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
