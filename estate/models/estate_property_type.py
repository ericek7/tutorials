from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Types"
    _order = "name"

    name = fields.Char("Name", required=True)
