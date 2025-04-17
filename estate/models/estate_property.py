from odoo import fields, models
from datetime import datetime, timedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "name"

    name = fields.Char("Name", required=True)
    description = fields.Text("Property Description")
    postcode = fields.Char("Postcode")
    date_available = fields.Date("Available From", copy=False, default=datetime.today() + timedelta(days=90))
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string="State",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        copy=False,
        default="new",
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer',
        copy=False,
    )
    salesman_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesman',
        default=lambda self: self.env.user,
    )
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type',
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string='Offers')
