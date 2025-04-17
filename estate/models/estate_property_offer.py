from odoo import fields, models, api
from datetime import date, timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price"

    price = fields.Float("Price")
    status = fields.Selection(
        string='Status',
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    create_date = fields.Date(string="Create Date", default=date.today())
    validity = fields.Integer("Validity (days)", default=7)
    deadline_date = fields.Date("Deadline", compute="_compute_deadline", inverse="_compute_inverse_deadline")

    @api.depends("create_date", "validity")
    def _compute_deadline(self):
        for record in self:
            record.deadline_date = record.create_date + timedelta(days=record.validity)

    @api.depends("create_date")
    def _compute_inverse_deadline(self):
        for record in self:
            record.validity = (record.deadline_date - record.create_date).days
