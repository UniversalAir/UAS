from odoo import api, models, fields, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_cart_info(self):
        super(SaleOrder, self)._compute_cart_info()
        for order in self:
            if order and order.pricelist_id and not order.pricelist_id.is_wholesale_pricelist:
                order.only_services = True