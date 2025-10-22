from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    current_user_group_ids = fields.Many2many(
        'res.groups',
        string='Current User Groups',
        compute='_compute_current_user_group_ids'
    )
    sent_to_cfo = fields.Boolean(default=False)
    approved_cfo = fields.Boolean(default=False)
    sent_to_ceo = fields.Boolean(default=False)
    approved_ceo = fields.Boolean(default=False)



    @api.depends('user_id')  # Assuming user_id is a field that triggers the compute
    def _compute_current_user_group_ids(self):
        for order in self:
            # Get the current user's groups
            order.current_user_group_ids = self.env.user.groups_id
            
            

    # def action_approve_cfo(self):
    #     if self.approval_state == 'waiting':
    #         self.write({
    #             'approved_cfo': True,
    #             'sent_to_ceo': False,
    #         })

    
    # def action_approve_coo(self):
    #     self['approval_state']='approve_coo'
    #     self['Approve_by_coo'] = self.write_uid.id
    #     self['approve_by_coo_timestamp'] = fields.Datetime.now()
    #     self['state'] = 'sent'

    #     self.write({
    #             'sent_to_ceo': True,
    #             'sent_to_cfo': True
    #         })

        


    # def send_to_cfo(self):
    #     self['approval_state']= 'waiting'
    #     self.write({
    #             'sent_to_ceo': True,
    #             'sent_to_cfo': True
    #         })

    
    # def send_to_ceo(self):
    #     self['approval_state']= 'approve_coo'
    #     self.write({
    #             'sent_to_ceo': True,
    #             'sent_to_cfo': True
    #         })


    def action_reject_sale_2(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'product.template',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }