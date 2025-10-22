from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class RfqComparison(models.Model):
    _inherit = "rfq.comparison"


    #Aneeq 42,990
    pr_field = fields.Boolean(
        string='Is PR Field Read-only',
        compute='_compute_pr_field_readonly',
    )

    @api.depends('purchase_request_id')
    def _compute_pr_field_readonly(self):
        for record in self:
            record.pr_field = record.po_approval_state in ['approve_ceo', 'done']
            
#Aneeq 42,990


    # state = fields.Selection(add_selection=[('cancel', 'Cancelled')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'POs Generated'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    def action_cancel(self):
        if self.env.user.login == 'ghufran.ali@biafo.com':
            self.write({'state': 'cancel'})

    def action_prepared(self):

        group_name = "AN.Checked_AN"
        group = self.env.ref(group_name)
        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Prepared State',
                note='The Approval Note has been set to the Prepared state and is ready for review.',
            )

        self['po_approval_state']='prepare'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        self['readonly_check']=True

    def action_verified(self):

        group_name = "AN.Verified_CFO_AN"
        group = self.env.ref(group_name)
        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Checked State',
                note='The Approval Note has been set to the Checked state and is ready for review.',
            )

        group_name_2 = "AN.Checked_AN"
        group2 = self.env.ref(group_name_2)

        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['po_approval_state']='verify'
            self['verified_by'] = self.write_uid.id
            self['verified_timestamp'] = fields.Datetime.now()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "rfq.comparison"),  # Related to the purchase request model
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

    def action_approve_by_cfo(self):

        group_name = "AN.Verfied_COO_AN"
        group = self.env.ref(group_name)
        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Verified CFO State',
                note='The Approval Note has been Verified by CFO and is ready for review.',
            )

        group_name_2 = "AN.Verified_CFO_AN"
        group2 = self.env.ref(group_name_2)

        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['po_approval_state']='approve_cfo'
            self['approve_by_cfo'] = self.write_uid.id
            self['approve_by_cfo_timestamp'] = fields.Datetime.now()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "rfq.comparison"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Order in Checked State')  # Match specific activity created in action_prepared
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

        group_name = "AN.Verified_CEO_AN"
        group = self.env.ref(group_name)
        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Verified COO State',
                note='The Approval Note has been Verified by COO and is ready for review.',
            )

        group_name_2 = "AN.Verfied_COO_AN"
        group2 = self.env.ref(group_name_2)

        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['po_approval_state']='approve_coo'
            self['approve_by_coo'] = self.write_uid.id
            self['approve_by_coo_timestamp'] = fields.Datetime.now()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "rfq.comparison"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Order in Verified CFO State')  # Match specific activity created in action_prepared
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

    def action_approve_by_ceo(self):

        group_name = "AN.After_Verified_CEO_AN"
        group = self.env.ref(group_name)
        # Create an activity for each user in the group
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order in Verified CEO State',
                note='The Approval Note has been Verified by CEO and is ready for review.',
            )

        group_name_2 = "AN.Verified_CEO_AN"
        group2 = self.env.ref(group_name_2)

        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:

            self['po_approval_state']='approve_ceo'
            self['approve_by_ceo'] = self.write_uid.id
            self['approve_by_ceo_timestamp'] = fields.Datetime.now()

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "rfq.comparison"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group2.users.ids),  # For users in the group2
                ('summary', '=', 'Order in Verified COO State')  # Match specific activity created in action_prepared
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

    def prepare_data_for_total(self,vendors_data,vendor_names):
        filtered_data = {}
        for i in vendors_data:
            for v in i.values():
                for j in v:
                    if j['name'] not in filtered_data:
                        filtered_data[j['name']]={
                            'total_untaxed':j['untaxed_subtotal'],
                            'total_taxed':j['taxed_subtotal'],
                        }
                        continue
                    filtered_data[j['name']]['total_untaxed']+=j['untaxed_subtotal']
                    filtered_data[j['name']]['total_taxed']+=j['taxed_subtotal']
        final_data = []
        for vendor in vendor_names:
            if vendor in filtered_data.keys():
                final_data.append({
                    'name':vendor,
                    'total_untaxed':filtered_data[vendor]['total_untaxed'],
                    'tax':filtered_data[vendor]['total_taxed'] - filtered_data[vendor]['total_untaxed'],
                    'total_taxed':filtered_data[vendor]['total_taxed'],
                })
            else:
                final_data.append({
                    'name':vendor,
                    'total_untaxed':0,
                    'tax':0,
                    'total_taxed':0,
                })
        return final_data


    # def sort_entries(self, data, sort_order):
    #     for key, entries in data[0].items():
    #         entries.sort(key=lambda x: sort_order.index(x["name"]) if x["name"] in sort_order else len(sort_order))


    #     raise UserError(f"{data} ======== {sort_order}")
    #     return data



    def sort_entries(self, data, sort_order):
        for item in data:  # Loop over all dictionaries in the list
            for key, entries in item.items():  # Iterate over each dictionary inside the list
                entries.sort(key=lambda x: sort_order.index(x["name"]) if x["name"] in sort_order else len(sort_order))
        # raise UserError(f"{data} ======== {sort_order}")
        return data






    def action_prepared(self):
        for rec in self:
            # Check PR Details
            for pr_detail in rec.pr_detail_ids:
                matching_line = rec.purchase_request_id.line_ids.filtered(
                    lambda line: line.product_id == pr_detail.product_id
                )
                if not matching_line:
                    continue

                # for line in matching_line:
                #     if pr_detail.product_qty > line.product_qty:
                #         raise ValidationError(
                #             f"The quantity for product {pr_detail.product_id.display_name} "
                #             f"({pr_detail.product_qty}) exceeds the requested quantity "
                #             f"({line.product_qty})."
                #         )

            # Check PO Details
            for po_detail in rec.po_detail_ids:
                matching_line = rec.purchase_request_id.line_ids.filtered(
                    lambda line: line.product_id == po_detail.product_id
                )
                if not matching_line:
                    continue

                # for line in matching_line:
                #     if po_detail.product_qty > line.product_qty:
                #         raise ValidationError(
                #             f"The quantity for product {po_detail.product_id.display_name} "
                #             f"({po_detail.product_qty}) exceeds the requested quantity "
                #             f"({line.product_qty})."
                #         )

        return super(RfqComparison, self).action_prepared()

