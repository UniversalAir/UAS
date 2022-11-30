from odoo import api, fields, models, tools, _
from odoo.addons.website.models import ir_http
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'

    def get_all_parent_categories(self):
        cate_ids = self.env['product.public.category'].search([('parent_id', '=', False)])
        return cate_ids

    def get_branded_categories(self):
        # import pdb;pdb.set_trace()
        cate_ids = self.env['product.public.category'].search([], limit=1)
        return cate_ids

    def get_is_new_arrival(self):
        # import pdb;pdb.set_trace()
        cate_ids = self.env['product.template'].search([('is_new_arrival','=',True)])
        return cate_ids

    def get_header_display_categories(self):
        cate_ids = self.env['product.public.category'].search([('is_display_header', '=', True)])
        return cate_ids

    def get_other_pricelist(self):
        pricelist = request.website.get_current_pricelist()
        pricelists_ids = self.get_pricelist_available()
        other = pricelists_ids.filtered(lambda x: x.id != pricelist.id and x.is_wholesale_pricelist == False)
        if len(other) > 1:
            return other[0]
        return other
        
    def _get_pricelist_available(self, req, show_visible=False):
        """ Return the list of pricelists that can be used on website for the current user.
        Country restrictions will be detected with GeoIP (if installed).
        :param bool show_visible: if True, we don't display pricelist where selectable is False (Eg: Code promo)
        :returns: pricelist recordset
        """
        website = ir_http.get_request_website()
        if not website:
            if self.env.context.get('website_id'):
                website = self.browse(self.env.context['website_id'])
            else:
                # In the weird case we are coming from the backend (https://github.com/odoo/odoo/issues/20245)
                website = len(self) == 1 and self or self.search([], limit=1)
        isocountry = req and req.session.geoip and req.session.geoip.get('country_code') or False
        partner = self.env.user.partner_id
        last_order_pl = partner.last_website_so_id.pricelist_id
        partner_pl = partner.property_product_pricelist
        pricelists = website._get_pl_partner_order(isocountry, show_visible,
                                                   website.user_id.sudo().partner_id.property_product_pricelist.id,
                                                   req and req.session.get('website_sale_current_pl') or None,
                                                   website.pricelist_ids,
                                                   partner_pl=partner_pl and partner_pl.id or None,
                                                   order_pl=last_order_pl and last_order_pl.id or None)

        pricelists_ids = self.env['product.pricelist'].browse(pricelists)
        if not partner_pl or not partner_pl.is_wholesale_pricelist:
            pricelists_ids = pricelists_ids.filtered(lambda x: x.is_wholesale_pricelist != True)
        else:
            wholesale_price_id = pricelists_ids.filtered(lambda x: x.is_wholesale_pricelist == True and partner_pl.id == x.id)
            if wholesale_price_id:
                request.session['website_sale_current_pl'] = wholesale_price_id[0].id
                return pricelists_ids.filtered(lambda x: (x.is_wholesale_pricelist == True and partner_pl.id == x.id) or x.is_wholesale_pricelist == False)
        return pricelists_ids

    @api.model
    def get_category_breadcum(self, category):
        data = []
        parent_categ = False
        if category:
            categ_data = self.env['product.public.category'].search([('id', '=', int(category))])
            data.append(categ_data)
            parent_categ = categ_data
            if categ_data and categ_data.parent_id:
                parent_categ = categ_data.parent_id
                data.append(parent_categ)
                while parent_categ.parent_id:
                    parent_categ = parent_categ.parent_id
                    data.append(parent_categ)
            data.reverse()
        return data

    # def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
    #     sale_order = super(Website, self).sale_get_order(force_create, code, update_pricelist, force_pricelist)
    #     if sale_order and sale_order.state == 'draft':
    #         if request.session.get('website_sale_current_pl'):
    #             sale_order.write({'pricelist_id': request.session.get('website_sale_current_pl')})
    #             sale_order.update_prices()

        if sale_order and sale_order.pricelist_id:
            category_dict ={}
            for line in sale_order.order_line:
                if line.product_id.categ_id.id in category_dict:
                    category_dict[line.product_id.categ_id.id] += line.product_uom_qty
                else:
                    category_dict[line.product_id.categ_id.id] = line.product_uom_qty

            for line in sale_order.order_line:
                if line.product_id.categ_id.id in category_dict:
                    quantity = category_dict.get(line.product_id.categ_id.id)

                    product_context={
                        'partner': sale_order.partner_id,
                        'quantity': quantity,
                        'date': sale_order.date_order,
                        'pricelist': sale_order.pricelist_id.id,
                    }
                    product = self.env['product.product'].with_context(product_context).with_company(sale_order.company_id.id).browse(line.product_id.id)
                    line.price_unit = float(product.price)
        return sale_order