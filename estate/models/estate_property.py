from odoo import fields, models, api, exceptions, tools
from datetime import datetime, timedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(
        string="Title",
        required=True
    )
    description = fields.Text(
        string="Property Description"
    )
    postcode = fields.Char(
        string="Postcode"
    )
    date_available = fields.Date(
        string="Available From",
        copy=False,
        default=datetime.today() + timedelta(days=90)
    )
    expected_price = fields.Float(
        string="Expected Price",
        required=True
    )
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2
    )
    living_area = fields.Integer(
        string="Living Area (sqm)"
    )
    facades = fields.Integer(
        string="Facades"
    )
    garage = fields.Boolean(
        string="Garage"
    )
    garden = fields.Boolean(
        string="Garden"
    )
    garden_area = fields.Integer(
        string="Garden Area (sqm)"
    )
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
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
        options="{'no_create': True, 'no_edit': True}",
    )
    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tag",
        options="{'color_field': 'color'}"
    )
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string='Offers'
    )
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area"
    )
    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_price"
    )

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be greater than 0.'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'The selling price must be greater than 0.'),
    ]

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

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.state == 'new' and record.offer_ids:
            record.state = 'offer_received'
        if record.state == 'offer_received' and not record.offer_ids:
            record.state = 'new'
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.state == 'new' and record.offer_ids:
                record.state = 'offer_received'
            if record.state == 'offer_received' and not record.offer_ids:
                record.state = 'new'
        return res

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if ((not tools.float_is_zero(record.selling_price, precision_digits=2)) and
                    tools.float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0):
                raise exceptions.ValidationError("The selling price must be at least 90% of the expected price.")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_new_or_cancelled(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise exceptions.ValidationError("You cannot delete a property unless its state is 'New' or 'Cancelled'.")

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