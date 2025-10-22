from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Field to store manual exchange rate
    manual_currency_rate_new = fields.Float(
        string='Manual Exchange Rate',
        digits=(12, 6),
        help="Manual exchange rate to use instead of the automatic one."
    )

    # Field to enable or disable manual rate
    use_manual_rate_new = fields.Boolean(
        string='Use Manual Rate',
        help="Use the manual exchange rate for this stock operation."
    )

    @api.constrains("manual_currency_rate_new_new")
    def _check_manual_currency_rate_new(self):
        """ Ensure manual exchange rate is not zero if manual rate is active """
        for record in self:
            if record.use_manual_rate_new and record.manual_currency_rate_new <= 0:
                raise UserError(_('Exchange Rate Field must be greater than zero when manual rate is used.'))

    # @api.onchange('use_manual_rate_new')
    # def _onchange_use_manual_rate_new(self):
    #     """ Handle changes to use_manual_rate_new """
    #     for record in self:
    #         # Access currency from related model if applicable
    #         picking_type_currency_id = record.picking_type_id.currency_id if hasattr(record, 'picking_type_id') else None
    #         company_currency_id = record.company_id.currency_id

    #         if record.use_manual_rate_new:
    #             if picking_type_currency_id == company_currency_id:
    #                 # Reset manual rate if company and picking currencies are the same
    #                 record.use_manual_rate_new = False
    #                 record.manual_currency_rate_new = 0  # Clear manual rate or set a default
    #                 raise UserError(_('Company currency and picking currency are the same. You cannot use a manual exchange rate for the same currency.'))

    @api.onchange('manual_currency_rate_new')
    def _onchange_manual_currency_rate_new(self):
        """ Apply currency rate or manual currency rate if manual rate is enabled """
        for rec in self:
            # Check if the manual rate should be used
            if rec.use_manual_rate_new:
                currency_rate = rec.manual_currency_rate_new
            else:
                # Fallback if currency_rate field is not available
                currency_rate = rec.currency_rate if hasattr(rec, 'currency_rate') else None
            
            if currency_rate:
                # Search for the related purchase orders
                purchase_order = self.env['purchase.order'].search([('name', '=', rec.origin)])
                for po in purchase_order:
                    if po.currency_id.id != 157:
                        # Search for the exchange rate record
                        rate = self.env['res.currency.rate'].search([
                            ('currency_id.id', '=', po.currency_id.id),
                            ('name', '=', datetime.datetime.now().date())
                        ])
                        if rate:
                            # Update the existing exchange rate record
                            rate.write({
                                'inverse_company_rate': currency_rate,
                                'currency_id': po.currency_id.id,
                            })
                        else:
                            # Create a new exchange rate record
                            self.env['res.currency.rate'].create({
                                'currency_id': po.currency_id.id,
                                'name': datetime.datetime.now().date(),
                                'inverse_company_rate': currency_rate,
                            })

        # Return an action to reload the page
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
