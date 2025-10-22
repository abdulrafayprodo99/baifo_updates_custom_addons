from odoo import models, fields, api,_
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit="purchase.order"

    cancel_note =  fields.Text(string="Cancel Note")

    def open_cancel_wizard(self):
        return {
            'name': _('Cancel Reason'),
            'res_model': 'cancel.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'purchase.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    # def button_cancel(self):
    #     for order in self:
    #         if self.env.user.login == 'ghufran.ali@biafo.com':
    #             if self.env.context.get('cancel',False):
    #                 return super(PurchaseOrder, self).button_cancel()
    #             order.open_cancel_wizard()




