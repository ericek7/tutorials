from odoo import api, models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_do_sell(self):
        res = super().action_do_sell()

        commission = self.selling_price * 0.06
        admin_fee = 100.00

        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Agency Commission',
                    'quantity': 1,
                    'price_unit': commission,
                }),
                (0, 0, {
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': admin_fee,
                }),
            ]
        }

        self.env['account.move'].create(invoice_vals)

        return res
