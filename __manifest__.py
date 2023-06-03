# -*- coding: utf-8 -*-
{
    'name': "Management of road shipments",

    'summary': "Road shipments management",

    'description': "Management of road shipments",

    'author': "SHINTHEO OU",
    'website': "http://www.shintheo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Shipping',
    'version': '3.0.2',
    'sequence': 10,

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'website_profile', 'base', 'mail', 'base_setup', 'product', 'analytic', 'digest', 'web', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir1.model.access.csv',
        'views/all_travels.xml',
        'views/hubkilo_bookings.xml',
        'views/hubkilo_messaging.xml',
        'views/hubkilo_travels.xml',
        # 'views/create_travel.xml',
        # 'views/edit_travel.xml',
        # 'views/user_all_travels.xml',
        # 'views/view_images.xml',
        # 'views/search.xml'
   ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
