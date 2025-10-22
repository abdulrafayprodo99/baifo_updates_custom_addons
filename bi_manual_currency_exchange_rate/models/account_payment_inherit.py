# # from odoo import models, fields, api, _
# # from odoo.exceptions import UserError

# # class AccountPayment(models.Model):
# #     _inherit = 'account.payment'

# #     # Field to store manual exchange rate
# #     manual_currency_rate = fields.Float(
# #         string='Manual Exchange Rate',
# #         digits=(12, 6),
# #         help="Manual exchange rate to use instead of the automatic one."
# #     )

# #     # Field to enable or disable manual rate
# #     use_manual_rate = fields.Boolean(
# #         string='Use Manual Rate',
# #         help="Use the manual exchange rate for this payment."
# #     )

# #     @api.constrains("manual_currency_rate")
# #     def _check_manual_currency_rate(self):
# #         """ Ensure manual exchange rate is not zero if manual rate is active """
# #         for record in self:
# #             if record.use_manual_rate and record.manual_currency_rate <= 0:
# #                 raise UserError(_('Exchange Rate Field must be greater than zero when manual rate is used.'))

# #     @api.onchange('use_manual_rate', 'currency_id')
# #     def check_currency_id(self):
# #         """ Ensure manual rate is only used when the currency differs from the company currency """
# #         if self.use_manual_rate and self.currency_id == self.company_id.currency_id:
# #             self.use_manual_rate = False
# #             raise UserError(_('Company currency and payment currency are the same. You cannot use a manual exchange rate for the same currency.'))
# #         else:
# #             self.currency_rate =  self.manual_currency_rate
# #             # raise UserError( self.currency_rate)

# #     def _compute_payment_amount(self, amount, currency, company_currency):
# #         """ Override to use manual currency rate if enabled """
# #         self.ensure_one()
# #         if self.use_manual_rate and self.manual_currency_rate:
# #             return amount / self.manual_currency_rate
# #         return super(AccountPayment, self)._compute_payment_amount(amount, currency, company_currency)

# #     # @api.constrains('use_manual_rate')
# #     # def currency_rate_change(self):
# #     #     raise UserError("Hello!!")
# #     #     """ Override to assign manual_currency_rate to currency_rate if manual rate is used """
# #     #     for payment in self:
# #     #         if payment.use_manual_rate and payment.manual_currency_rate:
# #     #             payment.currency_rate = payment.manual_currency_rate
# #     #         elif payment.currency_rate == 0:
# #     #             # If no manual rate is used and currency_rate is zero, set it to the default rate
# #     #             payment.currency_rate = payment.currency_id.rate





# from odoo import models, fields, api, _
# from odoo.exceptions import UserError

# class AccountPayment(models.Model):
#     _inherit = 'account.payment'

#     # Field to store manual exchange rate
#     manual_currency_rate = fields.Float(
#         string='Manual Exchange Rate',
#         digits=(12, 6),
#         help="Manual exchange rate to use instead of the automatic one."
#     )

#     # Field to enable or disable manual rate
#     use_manual_rate = fields.Boolean(
#         string='Use Manual Rate',
#         help="Use the manual exchange rate for this payment."
#     )

#     # Field for currency rate
#     currency_rate = fields.Float(
#         string='Currency Rate',
#         digits=(12, 6),
#         help="Exchange rate for the payment."
#     )

#     @api.constrains("manual_currency_rate")
#     def _check_manual_currency_rate(self):
#         """ Ensure manual exchange rate is not zero if manual rate is active """
#         for record in self:
#             if record.use_manual_rate and record.manual_currency_rate <= 0:
#                 raise UserError(_('Exchange Rate Field must be greater than zero when manual rate is used.'))

#     @api.onchange('use_manual_rate')
#     def _onchange_use_manual_rate(self):
#         """ Handle changes to use_manual_rate """
#         if self.use_manual_rate:
#             if self.currency_id == self.company_id.currency_id:
#                 # Reset manual rate if company and payment currencies are the same
#                 self.use_manual_rate = False
#                 self.currency_rate = 0  # Clear currency rate or set a default
#                 raise UserError(_('Company currency and payment currency are the same. You cannot use a manual exchange rate for the same currency.'))
#             else:
#                 # Set currency_rate to manual_currency_rate if manual rate is enabled
#                 self.currency_rate = self.manual_currency_rate if self.manual_currency_rate else 1.0
#         else:
#             # Optional: Clear or reset currency_rate if manual rate is not used
#             self.currency_rate = 0

#     def _create_payment_entry(self, amount):
#         """ Override to apply the manual currency rate in the journal entry """
#         # Call the original method to create the journal entry
#         move = super(AccountPayment, self)._create_payment_entry(amount)

#         # Apply the manual currency rate if enabled
#         if self.use_manual_rate and self.manual_currency_rate:
#             for line in move.line_ids:
#                 if line.currency_id and line.currency_id != self.company_id.currency_id:
#                     # Adjust the currency rate in the journal entry lines
#                     line.currency_rate = self.manual_currency_rate

#         return move

#     def action_post(self):
#         """ Override the post method to apply the manual currency rate in journal entries """
#         res = super(AccountPayment, self).action_post()

#         # Ensure manual currency rate is applied to all related journal entries
#         for payment in self:
#             if payment.use_manual_rate and payment.manual_currency_rate:
#                 for move in payment.move_line_ids.mapped('move_id'):
#                     for line in move.line_ids:
#                         if line.currency_id and line.currency_id != payment.company_id.currency_id:
#                             # Update the currency rate in the journal entry lines
#                             line.currency_rate = payment.manual_currency_rate

#         return res





from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Field to store manual exchange rate
    manual_currency_rate = fields.Float(
        string='Manual Exchange Rate',
        digits=(12, 6),
        help="Manual exchange rate to use instead of the automatic one."
    )

    # Field to enable or disable manual rate
    use_manual_rate = fields.Boolean(
        string='Use Manual Rate',
        help="Use the manual exchange rate for this payment."
    )

    @api.constrains("manual_currency_rate")
    def _check_manual_currency_rate(self):
        """ Ensure manual exchange rate is not zero if manual rate is active """
        for record in self:
            if record.use_manual_rate and record.manual_currency_rate <= 0:
                raise UserError(_('Exchange Rate Field must be greater than zero when manual rate is used.'))

    @api.onchange('use_manual_rate')
    def _onchange_use_manual_rate(self):
        """ Handle changes to use_manual_rate """
        if self.use_manual_rate:
            if self.currency_id == self.company_id.currency_id:
                # Reset manual rate if company and payment currencies are the same
                self.use_manual_rate = False
                self.manual_currency_rate = 0  # Clear manual rate or set a default
                raise UserError(_('Company currency and payment currency are the same. You cannot use a manual exchange rate for the same currency.'))

    # def action_post(self):
    #     """ Override to apply the manual currency rate in the journal entry """
    #     # Call the super method first to post the payment and create the journal entries
    #     res = super(AccountPayment, self).action_post()

    #     # Now that the payment is posted, apply the manual currency rate if enabled
    #     if self.use_manual_rate and self.manual_currency_rate:
    #         for move in self.move_id:  # Access the created move directly via move_id
    #             for line in move.line_ids:
    #                 if line.currency_id and line.currency_id != self.company_id.currency_id:
    #                     # Update the currency rate on journal lines
    #                     line.currency_rate = self.manual_currency_rate

    #     return res


    @api.onchange('manual_currency_rate')
    def _onchange_manual_currency_rate(self):
        """ Apply currency rate or manual currency rate if manual rate is enabled """
        for rec in self:
            # Use manual currency rate if enabled
            currency_rate = rec.manual_currency_rate if rec.use_manual_rate else rec.currency_rate
            
            if currency_rate:
                if rec.payment_type in ["outbound", "inbound"]:
                    if rec.currency_id.id != 157:  # Ensure the currency is not the company currency
                        rate = self.env['res.currency.rate'].search([
                            ('currency_id', '=', rec.currency_id.id),
                            ('name', '=', rec.date)
                        ])
                        
                        if rate:
                            rate.write({
                                'inverse_company_rate': currency_rate,
                                'currency_id': rec.currency_id.id,
                            })
                        else:
                            self.env['res.currency.rate'].create({
                                'currency_id': rec.currency_id.id,
                                'name': rec.date,
                                'inverse_company_rate': currency_rate,
                            })
        
        # Return an action to reload the page
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


