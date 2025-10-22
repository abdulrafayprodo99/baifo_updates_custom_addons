from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CancelPOWizard(models.TransientModel):
    _name = 'cancel.po.wizard'
    
    cancel_reason = fields.Text('Cancel Reason', required=True)

    def action_confirm(self):
        # Get the active purchase order from the context
        purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))

        # Ensure the order is not already canceled
        if purchase_order.state == 'cancel':
            raise UserError(_("This Purchase Order is already canceled."))

        # Set the cancel reason on the purchase order
        purchase_order.cancel_reason = self.cancel_reason

        # Call the original button_cancel method from the Purchase Order model
        purchase_order.button_cancel(from_wizard=True)

        # Close the wizard window
        return {'type': 'ir.actions.act_window_close'}