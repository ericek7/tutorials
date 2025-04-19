from odoo import fields, models, api, exceptions
from datetime import date, timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float(
        string="Price"
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ],
        copy=False,
        readonly=True,
        default='',
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True
    )
    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True
    )
    create_date = fields.Date(
        string="Create Date",
        default=date.today()
    )
    validity = fields.Integer(
        string="Validity (days)",
        default=7
    )
    deadline_date = fields.Date(
        string="Deadline",
        compute="_compute_deadline",
        inverse="_compute_inverse_deadline"
    )
    property_state = fields.Selection(
        related='property_id.state',
        store=True
    )
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', 'The offer price must be greater than 0.'),
    ]

    @api.depends("create_date", "validity")
    def _compute_deadline(self):
        for record in self:
            record.deadline_date = record.create_date + timedelta(days=record.validity)

    @api.depends("create_date")
    def _compute_inverse_deadline(self):
        for record in self:
            record.validity = (record.deadline_date - record.create_date).days

    def action_accept(self):
        if self.property_id.state == "sold":
            raise exceptions.UserError('Property is already sold.')
        if self.property_id.state == "cancelled":
            raise exceptions.UserError('Property is already cancelled.')
        if self.property_id.state == "offer_accepted":
            raise exceptions.UserError('An offer for the property is already accepted.')
        if self.state == 'refused':
            raise exceptions.UserError('Offer has been already refused.')
        self.state = "accepted"
        self.property_id.state = "offer_accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id
        return True

    def action_refuse(self):
        if self.state == 'accepted':
            raise exceptions.UserError('Offer has been already accepted.')
        self.state = "refused"
        return True