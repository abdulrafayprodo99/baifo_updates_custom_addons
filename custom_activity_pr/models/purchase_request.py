from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"



    def action_prepared(self):

        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            group_name = 'pr.Verify_opex_production_factory'
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.Recommended_opex_or_capex_factory'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name = 'pr.Checked_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.Recommended_opex_or_capex_factory'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name = 'pr.Checked_opex_or_capex_factory_headoffice'


        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Prepared State',
                note='The Purchase Request has been set to the prepared state and is ready for review.',
            )

        self['approval_state']='store_supervisors'
        self['headoffice_state']='store_supervisors'
        self['plant_state']='store_supervisors'
        self['main_state']='store_supervisors'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        # ubaid
        self['readonly_check'] = False
  



    def action_recommended(self):

        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.Checked_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            pass
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.Checked_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            pass

        group = self.env.ref(group_name)

        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Recommended State',
                note='The Purchase has been set to the Recommended state and is ready for review.',
            )
            
        summary = ""

        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name_2 = 'pr.Recommended_opex_or_capex_factory'
            summary='Order in Prepared State'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            pass
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name_2 = 'pr.Recommended_opex_or_capex_factory'
            summary='Order in Prepared State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            pass



                        # Fetch the specific group by reference
        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            # Update states and fields

            self['plant_state']= 'recommended_by'
            self['main_state']= 'recommended_by'
            self['recommended_by'] = self.write_uid.id
            self['recommended_by_timestamp'] = fields.Datetime.now()


            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
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





    def action_checked(self):
        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.Verify_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name = 'pr.Verify_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.Verify_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name = 'pr.Verify_opex_or_capex_factory_headoffice'



        group = self.env.ref(group_name)
                # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Checked State',
                note='The Purchase has been set to the Checked state and is ready for review.',
            )
        
        summary = ""


        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name_2 = 'pr.Checked_opex_or_capex_factory_headoffice'
            summary='Order in Recommended State'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name_2 = 'pr.Checked_opex_or_capex_factory_headoffice'
            summary='Order in Prepared State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name_2 = 'pr.Checked_opex_or_capex_factory_headoffice'
            summary='Order in Recommended State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name_2 = 'pr.Checked_opex_or_capex_factory_headoffice'
            summary='Order in Prepared State'


        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            # Update states and fields
        
            self['headoffice_state']='checked'
            self['plant_state']='checked'
            self['main_state']='checked'
            self['checked_by'] = self.write_uid.id
            self['checked_by_timestamp'] = fields.Datetime.now()

            # self.create_line_in_custom_budget() 

            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
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





    
    def action_verify(self):
        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            group_name = 'pr.Approved_opex_production_factory'
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.Reviewed_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name = 'pr.Reviewed_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.Reviewed_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name = 'pr.Reviewed_opex_or_capex_factory_headoffice'



        # Get the group (replace 'custom_module.group_team_lead' with your actual group XML ID)
        group = self.env.ref(group_name)

                # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Verified State',
                note='The Purchase has been set to the Verified state and is ready for review.',
            )

        summary = ""
        
        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            group_name_2 = 'pr.Verify_opex_production_factory'
            summary = 'Order in Prepared State'
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name_2 = 'pr.Verify_opex_or_capex_factory_headoffice'
            summary='Order in Checked State'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name_2 = 'pr.Verify_opex_or_capex_factory_headoffice'
            summary='Order in Checked State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name_2 = 'pr.Verify_opex_or_capex_factory_headoffice'
            summary='Order in Checked State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name_2 = 'pr.Verify_opex_or_capex_factory_headoffice'
            summary='Order in Checked State'

        

        # Fetch the specific group by reference
        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            # Update states and fields
            self['approval_state'] = 'verify'
            self['headoffice_state'] = 'verify'
            self['plant_state'] = 'verify'
            self['main_state'] = 'verify'
            self['verify_by'] = self.write_uid.id
            self['verify_timestamp'] = fields.Datetime.now()
            
            # Call the button action
            self.button_to_approve()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
                activities.unlink()

            # Reload the current view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # If the current user is not in the group2, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }




    def action_reviewed(self):

        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
        
        # Get the group (replace 'custom_module.group_team_lead' with your actual group XML ID)
        group = self.env.ref(group_name)

                # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Reviewed State',
                note='The Purchase has been set to the Reviewed state and is ready for Approval.',
            )
            
        summary = ""
        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            pass
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name_2 = 'pr.Reviewed_opex_or_capex_factory_headoffice'
            summary='Order in Verified State'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name_2 = 'pr.Reviewed_opex_or_capex_factory_headoffice'
            summary='Order in Verified State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name_2 = 'pr.Reviewed_opex_or_capex_factory_headoffice'
            summary='Order in Verified State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name_2 = 'pr.Reviewed_opex_or_capex_factory_headoffice'
            summary='Order in Verified State'
        



        # Fetch the specific group by reference
        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:

            self['headoffice_state']='reviewed'
            self['plant_state']='reviewed'
            self['main_state']='reviewed'
            self['reviewed_by'] = self.write_uid.id
            self['reviewed_by_timestamp'] = fields.Datetime.now()

            # self.button_to_approve()
             # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
                activities.unlink()

                # Reload the current view
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
        else:
            # If the current user is not in the group2, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }   
        

    
    # def action_approve(self):


    #     if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
    #         group_name = 'pr.Approved_opex_production_factory'
    #         summary='Order in Verified State'
    #     elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
    #         group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
    #         summary='Order in Reviewed State'
    #     elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
    #         group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
    #         summary='Order in Reviewed State'
    #     elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
    #         group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
    #         summary='Order in Reviewed State'
    #     elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
    #         group_name = 'pr.Approved_opex_or_capex_factory_headoffice'
    #         summary='Order in Reviewed State'

    #             # Fetch the specific group by reference
    #     group = self.env.ref(group_name)
        
    #     # Check if the current user belongs to the group
    #     if self.env.user.id in group.users.ids:
    #         self['approval_state']= 'approve'
    #         self['headoffice_state']= 'approve'
    #         self['plant_state']= 'approve'
    #         self['main_state']= 'approve'
    #         self['approve_by'] = self.write_uid.id
    #         self['approve_timestamp'] = fields.Datetime.now()
    #         self.button_approved()

    #                     # Search for specific activities related to this purchase request
    #         activities = self.env['mail.activity'].search([
    #             ('res_model', '=', "purchase.request"),  # Related to the purchase request model
    #             ('res_id', '=', self.id),  # For this specific request
    #             ('user_id', 'in', group.users.ids),  # For users in the group
    #             ('summary', '=', summary)  # Match specific activity created in action_prepared
    #         ])
            
    #         # Unlink the matched activities
    #         activities.unlink()

    #         # Reload the current view
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }
    #     else:
    #         # If the current user is not in the group, raise a warning or return a message
    #         return {
    #             'warning': {
    #                 'title': "Unauthorized Action",
    #                 'message': "You do not have the required permissions to perform this action.",
    #             }
    #         }




    def action_approve(self):

        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            group_name = 'pr.After_Approved_Group'
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name = 'pr.After_Approved_Group'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name = 'pr.After_Approved_Group'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name = 'pr.After_Approved_Group'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name = 'pr.After_Approved_Group'


        # Get the group (replace 'custom_module.group_team_lead' with your actual group XML ID)
        group = self.env.ref(group_name)

        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Request is Approved State',
                note='The Purchase has been set to the Approved state and is ready for Approval.',
            )
            
        summary = ""
        if self['pr_type'] == 'opex' and self['opex_type'] == 'production':
            group_name_2 = 'pr.Approved_opex_production_factory'
            summary='Order in Verified State'
        elif self['pr_type']  == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'plant':
            group_name_2 = 'pr.Approved_opex_or_capex_factory_headoffice'
            summary='Order in Reviewed State'
        elif self['pr_type'] == 'opex' and self['opex_type'] == 'consumable' and self['opex_sub_type'] == 'head_office': 
            group_name_2 = 'pr.Approved_opex_or_capex_factory_headoffice'
            summary='Order in Reviewed State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'plant': 
            group_name_2 = 'pr.Approved_opex_or_capex_factory_headoffice'
            summary='Order in Reviewed State'
        elif self['pr_type'] == 'capex' and self['capex_type'] == 'head_office': 
            group_name_2 = 'pr.Approved_opex_or_capex_factory_headoffice'
            summary='Order in Reviewed State'

                # Fetch the specific group by reference
        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['approval_state']= 'approve'
            self['headoffice_state']= 'approve'
            self['plant_state']= 'approve'
            self['main_state']= 'approve'
            self['approve_by'] = self.write_uid.id
            self['approve_timestamp'] = fields.Datetime.now()
            self.button_approved()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
                activities.unlink()

                # Reload the current view
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
        else:
            # If the current user is not in the group2, raise a warning or return a message
            return {
                'warning': {
                    'title': "Unauthorized Action",
                    'message': "You do not have the required permissions to perform this action.",
                }
            }
