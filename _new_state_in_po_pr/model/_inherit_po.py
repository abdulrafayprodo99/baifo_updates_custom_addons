from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class NewStateAtPoPr(models.Model):
    _inherit = "purchase.order"
    
    close_reason = fields.Text('Close Reason')
    cancel_reason = fields.Text('Cancel Reason')



    state = fields.Selection(
        selection_add=[
            ("close_po", "Close PO")
        ],
        ondelete={'close_po': 'cascade'}
    )

    def button_cancel(self,from_wizard=None):
        if from_wizard:
            return super().button_cancel()
        else:    
         return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.po.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }
         
    def action_close_pr(self):
        # self.state = 'close_po'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'close.po.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }

    # def write(self, vals):
    #     for record in self:
    #         if record.state == 'close_po':
    #             raise UserError(_("The PO is closed, you cannot edit any fields."))
    #         else:
    #             return super(NewStateAtPoPr, self).write(vals)

    def write(self, vals):
        # Retrieve all computed fields dynamically
        computed_fields = {
            name for name, field in self._fields.items() if field.compute
        }
        computed_fields.add('prepared_timestamp')
        # Check if `vals` only contains computed fields
        if set(vals.keys()).issubset(computed_fields):
            return super(NewStateAtPoPr, self).write(vals)

        for record in self:
            # Apply validation only for non-computed fields when state is 'close_po'
            if record.state == 'close_po':
                raise UserError(_("The PO is closed, you cannot edit any fields."))

        return super(NewStateAtPoPr, self).write(vals)