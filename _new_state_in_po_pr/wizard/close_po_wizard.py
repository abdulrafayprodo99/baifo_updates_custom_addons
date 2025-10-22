from odoo import models, fields, api

class ClosePOWizard(models.TransientModel):
    _name = 'close.po.wizard'

    close_reason = fields.Text('Close Reason', required=True)

    def action_confirm(self):
        # Get the active purchase order from context
        purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
        
        # Set the close reason on the purchase order
        purchase_order.close_reason = self.close_reason
        
        # Change the state of the purchase order to 'close_po'
        purchase_order.state = 'close_po'
        
        # Close the wizard window
        return {'type': 'ir.actions.act_window_close'}
