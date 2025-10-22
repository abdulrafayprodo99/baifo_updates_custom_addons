from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'




    def action_confirm(self):

        if self.category_id.name == "Advance Requisition - Plant":
            group_name = "AR.Verified_AR_Plant"
        if self.category_id.name == "Advance Requisition - HO General":
            group_name = "AR.Verified_AR_HO_General"
        if self.category_id.name == "Advance Requisition - HO Procurement":
            group_name = "AR.Verified_AR_HO_Pro"

        group = self.env.ref(group_name)
                # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Request in Verified State',
                note='The Approval Request has been set to the Verified state and is ready for review.',
            )

        # make sure that the manager is present in the list if he is required
        self.ensure_one()
        if self.category_id.manager_approval == 'required':
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
            if not employee.parent_id:
                raise UserError(_('This request needs to be approved by your manager. There is no manager linked to your employee profile.'))
            if not employee.parent_id.user_id:
                raise UserError(_('This request needs to be approved by your manager. There is no user linked to your manager.'))
            if not self.approver_ids.filtered(lambda a: a.user_id.id == employee.parent_id.user_id.id):
                raise UserError(_('This request needs to be approved by your manager. Your manager is not in the approvers list.'))
        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.", self.approval_minimum))
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))

        approvers = self.approver_ids
        if self.approver_sequence:
            approvers = approvers.filtered(lambda a: a.status in ['new', 'pending', 'waiting'])

            approvers[1:].status = 'waiting'
            approvers = approvers[0] if approvers and approvers[0].status != 'pending' else self.env['approval.approver']
        else:
            approvers = approvers.filtered(lambda a: a.status == 'new')

        approvers._create_activity()
        approvers.sudo().write({'status': 'pending'})
        self.sudo().write({'date_confirmed': fields.Datetime.now()})


    


    def action_approve(self, approver=None):


        if self.category_id.name == "Advance Requisition - Plant":
            group_name_2 = "AR.Approved_AR_Plant"
        if self.category_id.name == "Advance Requisition - HO General":
            group_name_2 = "AR.Approved_AR_HOs"
        if self.category_id.name == "Advance Requisition - HO Procurement":
            group_name_2 = "AR.Approved_AR_HOs"


        group2 = self.env.ref(group_name_2)


                    # Search for specific activities related to this purchase request
        activities = self.env['mail.activity'].search([
            ('res_model', '=', "approval.request"),  # Related to the purchase request model
            ('res_id', '=', self.id),  # For this specific request
            ('user_id', 'in', group2.users.ids),  # For users in the group2
            ('summary', '=', 'Request in Verified State')  # Match specific activity created in action_prepared
        ])

        # Unlink the matched activities
        activities.unlink()

        # Update the state to 'canceled' for the matched activities
        # for activity in activities:
        #   activity.action_feedback()  # This method will mark the activity as canceled



        group_name = "AR.After_Approved_AR"

        group = self.env.ref(group_name)
                # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Request in Approved State',
                note='The Approval Request has been set to the Approved state and is ready for review.',
            )

       
        
        # Check if the current user belongs to the group2
        # if self.env.user.id in group2.users.ids:
        self._ensure_can_approve()

        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'approved'})
        self.sudo()._update_next_approvers('pending', approver, only_next_approver=True)
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()



        # Reload the current view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    # # else:
    #     # If the current user is not in the group, raise a warning or return a message
    #     return {
    #         'warning': {
    #             'title': "Unauthorized Action",
    #             'message': "You do not have the required permissions to perform this action.",
    #         }
    #     }
