from odoo import _, api, fields, models
import logging
from odoo.exceptions import ValidationError,UserError

_logger = logging.getLogger(__name__)

class NewStateAtPoPr(models.Model):
    _inherit = "purchase.request"

    check_user_exists_in_group = fields.Boolean(compute='visible_reset_button')

    def open_cancel_wizard(self):
        return {
            'name': _('Cancel Reason'),
            'res_model': 'cancel.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'purchase.request',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    def reset_to_approve(self):
        for rec in self:
            if rec.approval_state == 'close_pr':
                rec.approval_state = 'approve'

    def visible_reset_button(self):
        """
        Computes the visibility state of the reset button based on specific conditions.
        This function determines whether the reset button should be visible or not,
        by evaluating certain attributes or states of the record.
        """
        for rec in self:
            if rec.env.user.has_group('_new_state_in_po_pr.group_which_can_set_pr_state'):
                rec.check_user_exists_in_group = True
            else:
                rec.check_user_exists_in_group = False

            
# class _Purchase