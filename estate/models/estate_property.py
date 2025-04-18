from odoo import fields, models, api, exceptions
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
        readonly=True,
        default="new",
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer',
        copy=False,
        readonly=True,
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
    total_area = fields.Integer("Total Area (sqm)", compute="_compute_total_area")
    best_price = fields.Float("Best Offer", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if not record.offer_ids:
                record.best_price = 0
            else:
                record.best_price = max(offer.price for offer in record.offer_ids)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = ''
            self.garden_area = 0

    @api.onchange("salesman_id")
    def _onchange_salesman(self):
        self.name = f'House of {self.salesman_id.name}'
        self.description = f'This house is being sold by {self.salesman_id.name}'

    def action_do_sell(self):
        if self.state == 'cancelled':
            raise exceptions.UserError('Cancelled properties cannot be sold.')
        self.state = "sold"
        return True

    def action_do_cancel(self):
        if self.state == 'sold':
            raise exceptions.UserError('Sold properties cannot be cancelled.')
        self.state = "cancelled"
        return True