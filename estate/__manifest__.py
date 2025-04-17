{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'estate',
    'application': True,
    'website': 'https://www.odoo.com/page/estate',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_menus.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
    ],
}