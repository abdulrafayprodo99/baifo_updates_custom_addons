# from odoo import api, Command, fields, models, _
# from odoo.exceptions import UserError, ValidationError

# from collections import defaultdict

# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     def action_prepared(self):
#         group_name = 'SQ.Verified_SQ'
#         group = self.env.ref(group_name)

#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation in Prepared State',
#                 note='The Sale_Quotation has been set to the prepared state and is ready for review.',
#             )


#         self['approval_state']='prepared'
#         self['prepared_by'] = self.write_uid.id
#         self['prepared_timestamp'] = fields.Datetime.now()
#         self['readonly_check'] = True

    


#     def action_verify(self):
#         group_name = 'SQ.Approved_SQ_CFO'
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation in Verified State',
#                 note='The Sale_Quotation has been set to the Verified state and is ready for review.',
#             )

#         group_name_2 = "SQ.Verified_SQ"

#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:
#             self['approval_state'] = 'verify'
#             self['verify_by'] = self.env.user.id
#             self['verify_by_timestamp'] = fields.Datetime.now()


#             # Search for specific activities related to this purchase request
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the purchase request model
#                 ('res_id', '=', self.id),  # For this specific request
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation in Prepared State')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }
        
#     def action_approve_coo(self):
        
#         group_name = "SQ.After_Approve_SQ"
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation is Approved',
#                 note='The Sale_Quotation has been Approved  and is ready for review.',
#             )

#         group_name_2 = "SQ.Approved_SQ_CFO"
#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:
#             self['approval_state']='approve_coo'
#             self['Approve_by_coo'] = self.write_uid.id
#             self['approve_by_coo_timestamp'] = fields.Datetime.now()
#             self['state'] = 'sent'

#             self.write({
#                     'sent_to_ceo': True,
#                     'sent_to_cfo': True
#                 })
            
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the sale order model
#                 ('res_id', '=', self.id),  # For this specific order
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation in Verified State')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }



#     def send_to_cfo(self):

#         group_name = 'SQ.Send_SQ_CFO'
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation is Waiting For Approval CFO',
#                 note='The Sale_Quotation has been set to the Waiting state and is ready for review.',
#             )


#         group_name_2 = "SQ.Approved_SQ_CFO"

#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:

#             self['approval_state']= 'waiting'
#             self.write({
#                     'sent_to_ceo': True,
#                     'sent_to_cfo': True
#                 })


#             # Search for specific activities related to this purchase request
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the purchase request model
#                 ('res_id', '=', self.id),  # For this specific request
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation in Verified State')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }


    
#     def send_to_ceo(self):
#         group_name = 'SQ.Send_SQ_CEO'
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation is Waiting For Approval CEO',
#                 note='The Sale_Quotation has been set to the Waiting state and is ready for review.',
#             )


#         group_name_2 = "SQ.Send_SQ_Back"

#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:
#             self['approval_state']= 'approve_coo'
#             self.write({
#             'sent_to_ceo': True,
#             'sent_to_cfo': True
#             })

#             # Search for specific activities related to this purchase request
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the purchase request model
#                 ('res_id', '=', self.id),  # For this specific request
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation in Waiting State and Approved by CFO')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }


    
#     def action_approve_cfo(self):


#         group_name = 'SQ.Send_SQ_Back'
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation in Waiting State and Approved by CFO',
#                 note='The Sale_Quotation has been Approved by CFO and is ready for review.',
#             )


#         group_name_2 = "SQ.Send_SQ_CFO"

#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:
#             if self['approval_state'] == 'waiting':
#                 self['approval_state']= 'verify'
#                 self.write({
#                     'approved_cfo': True,
#                     'sent_to_ceo': False,
#                 })
#             else :
#                 self['approval_state']='approve_cfo'
            
#             self['Approve_by_cfo'] = self.write_uid.id
#             self['approve_by_cfo_timestamp'] = fields.Datetime.now()

#             # Search for specific activities related to this purchase request
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the purchase request model
#                 ('res_id', '=', self.id),  # For this specific request
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation is Waiting For Approval CFO')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }

        
#     def action_approve_ceo(self):

        

#         group_name = "SQ.After_Approve_SQ"
#         group = self.env.ref(group_name)
#         for user in group.users:
#             self.activity_schedule(
#                 'mail.mail_activity_data_todo',  # Activity type
#                 user_id=user.id,  # Assign the activity to each user in the group
#                 summary='Quotation is Approved',
#                 note='The Sale_Quotation has been Approved  and is ready for review.',
#             )

#         group_name_2 = "SQ.Send_SQ_CEO"

#         group2 = self.env.ref(group_name_2)
        
#         # Check if the current user belongs to the group2
#         if self.env.user.id in group2.users.ids:
#             self['approval_state']='approve_ceo'
#             self['Approve_by_ceo'] = self.write_uid.id
#             self['approve_by_ceo_timestamp'] = fields.Datetime.now()
#             self['state'] = 'sent'

#             # Search for specific activities related to this purchase request
#             activities = self.env['mail.activity'].search([
#                 ('res_model', '=', "sale.order"),  # Related to the purchase request model
#                 ('res_id', '=', self.id),  # For this specific request
#                 ('user_id', 'in', group2.users.ids),  # For users in the group2
#                 ('summary', '=', 'Quotation is Waiting For Approval CEO')  # Match specific activity created in action_prepared
#             ])
            
#             # Unlink the matched activities
#             activities.unlink()

#             # Reload the current view
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
#         else:
#             # If the current user is not in the group, raise a warning or return a message
#             return {
#                 'warning': {
#                     'title': "Unauthorized Action",
#                     'message': "You do not have the required permissions to perform this action.",
#                 }
#             }



from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_prepared(self):
        group_name = 'SQ.Verified_SQ'
        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation in Prepared State',
                note='The Sale_Quotation has been set to the prepared state and is ready for review.',
            )


        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True

    


    def action_verify(self):
        group_name = 'SQ.Approved_SQ_CFO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation in Verified State',
                note='The Sale_Quotation has been set to the Verified state and is ready for review.',
            )

        group_name_2 = "SQ.Verified_SQ"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state'] = 'verify'
            self['verify_by'] = self.env.user.id
            self['verify_by_timestamp'] = fields.Datetime.now()


            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation in Prepared State')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }
        
    def action_approve_coo(self):
        
        group_name = "SQ.Prepared_SQ"
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation is Approved',
                note='The Sale_Quotation has been Approved  and is ready for review.',
            )

        group_name_2 = "SQ.Approved_SQ_CFO"
        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state']='approve_coo'
            self['Approve_by_coo'] = self.write_uid.id
            self['approve_by_coo_timestamp'] = fields.Datetime.now()
            self['state'] = 'sent'

            self.write({
                    'sent_to_ceo': True,
                    'sent_to_cfo': True
                })
            
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the sale order model
                ('res_id', '=', self.id),  # For this specific order
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation in Verified State')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }



    def send_to_cfo(self):

        group_name = 'SQ.Send_SQ_CFO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation is Waiting For Approval CFO',
                note='The Sale_Quotation has been set to the Waiting state and is ready for review.',
            )


        group_name_2 = "SQ.Approved_SQ_CFO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:

            self['approval_state']= 'waiting'
            self.write({
                    'sent_to_ceo': True,
                    'sent_to_cfo': True
                })


            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation in Verified State')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }


    
    def send_to_ceo(self):
        group_name = 'SQ.Send_SQ_CEO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation is Waiting For Approval CEO',
                note='The Sale_Quotation has been set to the Waiting state and is ready for review.',
            )


        group_name_2 = "SQ.Send_SQ_Back"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state']= 'approve_coo'
            self.write({
            'sent_to_ceo': True,
            'sent_to_cfo': True
            })

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation in Waiting State and Approved by CFO')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }


    
    def action_approve_cfo(self):


        group_name = 'SQ.Send_SQ_Back'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation in Waiting State and Approved by CFO',
                note='The Sale_Quotation has been Approved by CFO and is ready for review.',
            )


        group_name_2 = "SQ.Send_SQ_CFO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            if self['approval_state'] == 'waiting':
                self['approval_state']= 'verify'
                self.write({
                    'approved_cfo': True,
                    'sent_to_ceo': False,
                })
            else :
                self['approval_state']='approve_cfo'
            
            self['Approve_by_cfo'] = self.write_uid.id
            self['approve_by_cfo_timestamp'] = fields.Datetime.now()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation is Waiting For Approval CFO')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }

        
    def action_approve_ceo(self):

        

        group_name = "SQ.Prepared_SQ"
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Quotation is Approved',
                note='The Sale_Quotation has been Approved  and is ready for review.',
            )

        group_name_2 = "SQ.Send_SQ_CEO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state']='approve_ceo'
            self['Approve_by_ceo'] = self.write_uid.id
            self['approve_by_ceo_timestamp'] = fields.Datetime.now()
            self['state'] = 'sent'

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation is Waiting For Approval CEO')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }


    def action_prepared_sale(self):

        group_name = 'SQ.Verified_SQ'
        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Prepared State',
                note='The Sale_Quotation has been set to the prepared SO state and is ready for review.',
            )

        group_name_2 = "SQ.Prepared_SQ"

        group2 = self.env.ref(group_name_2)

         # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state_sale']='prepared'
            self['prepare_sale'] = self.write_uid.id
            self['prepare_sale_timestamp'] = fields.Datetime.now()
            self['readonly_check'] = True

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Quotation is Approved')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }
    
    
    def action_verify_sale(self):
        group_name = 'SO.Approved_SO'
        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Verified SO State',
                note='The Sale Order has been set to the Verified SO state and is ready for review.',
            )

        group_name_2 = "SQ.Verified_SQ"

        group2 = self.env.ref(group_name_2)

        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state_sale']='verify'
            self['verified_sale'] = self.write_uid.id
            self['verified_sale_timestamp'] = fields.Datetime.now()

                        # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Order in Prepared State')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }

        
    def action_approve_sale(self):

        group_name = 'SQ.After_Approve_SQ'
        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Approved SO State',
                note='The Sale Order has been set to the Approved SO state and is ready for review.',
            )
        group_name_2 = "SO.Approved_SO"

        group2 = self.env.ref(group_name_2)

        if self.env.user.id in group2.users.ids:

            self['approval_state_sale']='approve'
            self['approve_sale'] = self.write_uid.id
            self['approve_sale_timestamp'] = fields.Datetime.now()
            self.action_confirm()

            activities = self.env['mail.activity'].search([
                ('res_model', '=', "sale.order"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Order in Verified SO State')  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }
