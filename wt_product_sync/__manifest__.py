# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Migrate Products",
    "version": "16.0.1.0",
    "category": "sale",
    "summary": "Allow to sync product between two odoo database",
    "description": """
    Migrate Products From 16 to 16, 15 to 16, 14 to 16
    """,
    "author": "Warlock Technologies Pvt Ltd.",
    "website": "http://warlocktechnologies.com",
    "support": "info@warlocktechnologies.com",
    "depends": ["stock", "sale_management", "purchase", "website", "website_sale", "mrp"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "wizard/message_view.xml",
        "views/product_sync_view.xml",
        "views/product_template_view.xml",
    ],
    "images": ["images/screen_image.png"],
    "license": "OPL-1",
    "installable": True,
}
