from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # active = fields.Boolean(default=True, string='Active')
    
    @api.onchange('name')
    def onchange_name(self):
        for rec in self:
            rec.mapped('move_ids').write({
                'origin':rec.name,
                'reference':rec.name
            })

            
    def set_to_null(self):
        if self.state != 'done':
            self.sudo().write({
                'state': 'assigned',
                'approval_state': False,
                'prepared_by1':False,
                'prepared_by_2':False,
                'verify_by':False,
                'verify_by1':False,
                'Approve_by':False,
                'approve_by1':False,
                'readonly_check':False,
                'dispatch_approval':False,
                'prepared_timestamp':False,
                'prepared_timestamp1':False,
                'verify_timestamp':False,
                'verify_timestamp1':False,
                'approve_timestamp':False,
                'approve_timestamp1':False,
                })

    def _action_generate_backorder_wizard(self, show_transfers=False, **kwargs):
        prepare = kwargs.get('prepare', False)
        view = self.env.ref('stock.view_backorder_confirmation')
        return {
            'name': _('Create Backorder?'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.backorder.confirmation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': dict(self.env.context, default_show_transfers=show_transfers, default_pick_ids=[(4, p.id) for p in self], default_prepare=prepare),
        }

    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        if not self.env.context.get('prepare',False):
            return super(StockPicking,self)._create_backorder()
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']
        for picking in self:
            if self.env.context.get('prepare',False) == True:
                moves_to_backorder = picking.move_ids.filtered(lambda x: x.state not in ('done', 'cancel') and (x.dispatch_approval not in ('prepared', 'checked','verify','approved') or x.approval_state not in ('prepared', 'checked','verify','approved')))
            else:
                moves_to_backorder = picking.move_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_ids': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                    'gate_in_id':False,
                })

                picking.message_post(
                    body=_('The backorder %s has been created.', backorder_picking._get_html_link())
                )
                # raise UserError(str(moves_to_backorder))
                moves_to_backorder.write({'picking_id': backorder_picking.id})
                moves_to_backorder.move_line_ids.package_level_id.write({'picking_id':backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                backorders |= backorder_picking
                if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                    bo_to_assign |= backorder_picking
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders

    def action_prepare1(self):
        # raise UserError("Reaching here")
        group_name = 'DO.Checked_DO_HO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order is Prepared HO State',
                note='The Sale_Quotation has been is set to Prepared HO state and is ready for review.',
            )
        if not self.env.context.get('prepare',False):
            pickings_to_backorder = self._check_backorder()
            if pickings_to_backorder:
                # self['dispatch_approval'] = 'prepared'
                # self['prepared_by1'] = self.write_uid.id
                # self['prepared_timestamp1'] = fields.Datetime.now()
                # self['readonly_check'] = True
                # # Check if the operation is a Delivery Order (DO)
                # if self.picking_type_id.code == 'outgoing':
                #     self.compute_temp_no()
                return pickings_to_backorder._action_generate_backorder_wizard(show_transfers=self._should_show_transfers(),prepare=True)
        self['dispatch_approval'] = 'prepared'
        self['prepared_by1'] = self.write_uid.id
        self['prepared_timestamp1'] = fields.Datetime.now()
        self['readonly_check'] = True

        # Check if the operation is a Delivery Order (DO)
        if self.picking_type_id.code == 'outgoing':
            self.compute_temp_no()

        
    def action_checked1(self):


        group_name = 'DO.Verified_DO_HO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order is Checked HO State',
                note='The Sale_Quotation has been is set to Checked HO state and is ready for review.',
            )

        group_name_2 = "DO.Checked_DO_HO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:

            self['dispatch_approval']='checked'
            self['checked_by1'] = self.write_uid.id
            self['checked_timestamp1'] =fields.Datetime.now()

            activities = self.env['mail.activity'].search([
                    ('res_model', '=', "stock.picking"),  # Related to the sale order model
                    ('res_id', '=', self.id),  # For this specific order
                    ('user_id', 'in', group2.users.ids),  # For users in the group2
                    ('summary', '=', 'Order is Prepared HO State')  # Match specific activity created in action_prepared
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




    def action_verify1(self):
        group_name = 'DO.Approved_DO_HO'
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,  # Assign the activity to each user in the group
                summary='Order is Verified HO State',
                note='The Sale_Quotation has been is set to Verified HO state and is ready for review.',
            )


        group_name_2 = "DO.Verified_DO_HO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['dispatch_approval']='verify'
            self['verify_by1'] = self.write_uid.id
            self['verify_timestamp1'] =fields.Datetime.now()


            activities = self.env['mail.activity'].search([
                    ('res_model', '=', "stock.picking"),  # Related to the sale order model
                    ('res_id', '=', self.id),  # For this specific order
                    ('user_id', 'in', group2.users.ids),  # For users in the group2
                    ('summary', '=', 'Order is Checked HO State')  # Match specific activity created in action_prepared
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





        
        
    def action_approve1(self):

        if self.picking_type_id.code == "outgoing":
            group_name = 'DO.Prepared_DO_P'
            group = self.env.ref(group_name)
            for user in group.users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',  # Activity type
                    user_id=user.id,  # Assign the activity to each user in the group
                    summary='Order is Approved HO State',
                    note='The Sale_Quotation has been is set to Approved HO state and is ready for review.',
                )



        group_name_2 = "DO.Approved_DO_HO"

        group2 = self.env.ref(group_name_2)
        
        # Check if the current user belongs to the group2
        if self.env.user.id in group2.users.ids:
            self['dispatch_approval']='approved'
            self['approve_by1'] = self.write_uid.id
            self['approve_timestamp1'] = fields.Datetime.now()

            activities = self.env['mail.activity'].search([
                    ('res_model', '=', "stock.picking"),  # Related to the sale order model
                    ('res_id', '=', self.id),  # For this specific order
                    ('user_id', 'in', group2.users.ids),  # For users in the group2
                    ('summary', '=', 'Order is Verified HO State')  # Match specific activity created in action_prepared
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

    
    # def action_prepare2(self):

    #     if self.picking_type_id.code == "outgoing":
    #         group_name = 'DO.Verified_DO_P'
    #         group = self.env.ref(group_name)
    #         for user in group.users:
    #             self.activity_schedule(
    #                 'mail.mail_activity_data_todo',  # Activity type
    #                 user_id=user.id,  # Assign the activity to each user in the group
    #                 summary='Order is Prepared P State',
    #                 note='The Sale_Quotation has been set to Prepared P state and is ready for review.',
    #             )

    #         group_name_2 = "DO.Prepared_DO_P"
    #         group2 = self.env.ref(group_name_2)
            
    #         # Check if the current user belongs to the group2
    #         if self.env.user.id in group2.users.ids:
    #             self['approval_state'] = 'prepared'
    #             self['prepared_by_2'] = self.write_uid.id
    #             self['prepared_timestamp'] = fields.Datetime.now()

    #             # Check if the operation is an internal transfer
    #             if self.picking_type_id.code != 'outgoing':
    #                 self.compute_temp_no()

    #             # Search for matching activities
    #             activities = self.env['mail.activity'].search([
    #                 ('res_model', '=', "stock.picking"),  # Related to the sale order model
    #                 ('res_id', '=', self.id),  # For this specific order
    #                 ('user_id', 'in', group2.users.ids),  # For users in the group2
    #                 ('summary', '=', 'Order is Approved HO State')  # Match specific activity created in action_prepared
    #             ])
                
    #             # Check if any activities are found before unlinking
    #             if activities:
    #                 activities.unlink()

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
    #     else:
    #         self['approval_state'] = 'prepared'
    #         self['prepared_by_2'] = self.write_uid.id
    #         self['prepared_timestamp'] = fields.Datetime.now()

    #         # Check if the operation is an internal transfer
    #         if self.picking_type_id.code != 'outgoing':
    #             self.compute_temp_no()


    def button_validate(self):
        
        for rec in self:
            if rec.picking_type_id.name == 'Inventory Transfer - Quarantine to WH':
                if not rec.backorder_id:
                    raise UserError("It is not possible to validate a quarantine picking that has no backorder.")
                landed_cost = self.env['stock.landed.cost'].search([])
                landed_cost = landed_cost.filtered(lambda x: rec.backorder_id.id in x.picking_ids.ids)
                if not landed_cost:
                    raise UserError("It is not possible to validate a quarantine picking that has no landed cost.")

            if rec.picking_type_id.name == 'GRN Imports':
                if not self.env.context.get('prepare',False):

                    dest_loc = self.env['stock.location'].sudo().search([('name','=','Main Store')]).id
                    pick_type = self.env['stock.picking.type'].search([('name', '=', 'Inventory Transfer - Quarantine to WH')], limit=1).id
                    backorder_vals = rec.copy_data()
                    for i in backorder_vals:
                        i.update({
                            'name':'/',
                            'location_id':rec.location_dest_id.id,
                            'location_dest_id':dest_loc,
                            'backorder_id':rec.id,
                            'import_grn_ref':rec.name,
                            'picking_type_id':pick_type,
                            'temp_name':'',
                            'move_ids':[(0,0,{
                                        'name': line.name,
                                        'date': line.date,
                                        'company_id': line.company_id.id,
                                        'product_id': line.product_id.id,
                                        # 'product_qty': line.product_qty,
                                        'product_uom_qty': line.product_uom_qty,
                                        'product_uom': line.product_uom.id,
                                        'location_id': rec.location_dest_id.id,
                                        'location_dest_id': dest_loc,
                                        'partner_id': line.partner_id.id if line.partner_id else False,
                                        'price_unit': line.price_unit,
                                        'origin': line.origin,
                                        'picking_type_id': pick_type,
                                        'quantity_done': line.quantity_done,
                                        'reserved_availability': 0.0,
                                        'reference': line.reference,
                                    })
                                    for line in rec.move_ids
                                ]
                            })
                    
                    backorder = self.sudo().create(backorder_vals)
                    backorder.action_confirm()
                    backorder.do_unreserve()
                    backorder.sudo().write({
                        'state':'assigned'
                    })

        return super().button_validate() 

    def action_prepare2(self):
        for rec in self:
            if not self.env.context.get('prepare',False):
                pickings_to_backorder = self._check_backorder()
                if pickings_to_backorder:
                    return pickings_to_backorder._action_generate_backorder_wizard(show_transfers=self._should_show_transfers(),prepare=True)
            # for line in rec.move_ids_without_package:
            #     if line.quantity_done == 0:
            #         raise UserError("Done Quantiy cannot be zero. Please set proper quantities before proceeding.")
            # for line in rec.move_line_ids_without_package:
            #     if line.qty_done == 0:
            #         raise UserError("Done Quantiy cannot be zero. Please set proper quantities before proceeding.")
            # # Check if any move line has qty_done = 0
            # if any(move_line.qty_done == 0 for move in rec.move_ids for move_line in move.move_line_ids):
            #     raise UserError("Done Quantiy cannot be zero. Please set proper quantities before proceeding.")


            # if rec.picking_type_id.name == "GRN Imports":
            #     pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
            #     if self.env.context.get('picking_ids_not_to_backorder'):
            #         pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
            #             lambda p: p.picking_type_id.create_backorder != 'always'
            #         )
            #     pickings_to_backorder = self - pickings_not_to_backorder
            #     pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
            #     pick_type = rec.env['stock.picking.type'].search([('name', '=', 'Inventory Transfer - Quarantine to WH')], limit=1)
                
            #     picking = pickings_to_backorder.copy({
            #         'name': '/',
            #         # 'move_ids': [],
            #         # 'move_line_ids': [],
            #         'backorder_id': pickings_to_backorder.id,
            #         'picking_type_id': pick_type.id,
            #         'import_grn_ref': rec.name
            #     })
            #     rec.write({
            #         'approval_state' : 'prepared',
            #         'prepared_by_2' : self.write_uid.id,
            #         'prepared_timestamp' : fields.Datetime.now()
            #     })
            #     return picking.action_confirm()

            # Check for picking type ID and match specific conditions
            if rec.picking_type_id.name == 'Inventory Transfer - Quarantine to WH':
                # Check for associated stock.landed.cost records
                landed_costs = self.env['stock.landed.cost'].search([
                    ('picking_ids.name', '=', rec.import_grn_ref),
                ])
                if not landed_costs:
                    raise UserError("No associated landed costs found for this picking.")
                # Ensure none are in 'posted' state
                if any(cost.state != 'done' for cost in landed_costs):
                    # Prepare detailed information for all landed cost records
                    landed_cost_info = '\n'.join(
                        [f"Name: {cost.name}, State: {cost.state}" for cost in landed_costs if cost.state != 'done']
                    )
                    raise UserError(
                        f"The following landed costs are associated with this picking and are not in the 'posted' state:\n{landed_cost_info}."
                    )
            # Common outgoing-related actions for both conditions
            if rec.picking_type_id.code == "outgoing":
                self._schedule_activity_for_group('DO.Verified_DO_P', 'Order is Prepared P State', 
                                                'The Sale_Quotation has been set to Prepared P state and is ready for review.')
            
                # Prepare for users in DO.Prepared_DO_P group
                if self._is_user_in_group("DO.Prepared_DO_P"):
                    self._set_prepared_state()
                    self._clear_related_activities('Order is Approved HO State')

                    # New code to check related stock moves
                    for move in rec.move_ids:
                        move.origin = rec.name  # Assign picking_id.name to origin
                        # New code to update reference for stock valuation layers
                        for valuation_layer in move.stock_valuation_layer_ids:
                            valuation_layer.reference = rec.name  # Assign rec.name to reference

                    return {'type': 'ir.actions.client', 'tag': 'reload'}
                else:
                    return {'warning': {'title': "Unauthorized Action", 
                                        'message': "You do not have the required permissions to perform this action."}}
            rec.compute_temp_no()
            # For non-outgoing or internal transfers
            self._set_prepared_state()
                                # New code to check related stock moves
            for move in rec.move_ids:
                    move.origin = rec.name  # Assign picking_id.name to origin

                    # New code to update reference for stock valuation layers
                    for valuation_layer in move.stock_valuation_layer_ids:
                        valuation_layer.reference = rec.name  # Assign rec.name to reference
            
    def _schedule_activity_for_group(self, group_name, summary, note):
        """Schedules an activity for all users in the specified group."""
        group = self.env.ref(group_name)
        for user in group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',  # Activity type
                user_id=user.id,
                summary=summary,
                note=note,
            )

    def _is_user_in_group(self, group_name):
        """Checks if the current user is in the specified group."""
        group = self.env.ref(group_name)
        return self.env.user.id in group.users.ids

    def _set_prepared_state(self):
        """Sets the prepared state fields."""
        self['approval_state'] = 'prepared'
        self['prepared_by_2'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        
        # Check for internal transfer operations
        if self.picking_type_id.code != 'outgoing':
            self.compute_temp_no()

    def _clear_related_activities(self, activity_summary):
        """Removes related activities based on a specific summary."""
        activities = self.env['mail.activity'].search([
            ('res_model', '=', "stock.picking"),
            ('res_id', '=', self.id),
            ('user_id', 'in', self.env.ref("DO.Prepared_DO_P").users.ids),
            ('summary', '=', activity_summary)
        ])
        if activities:
            activities.unlink()



        # raise UserError(self.picking_type_id.code)



    
    def action_verify(self):


        if self.picking_type_id.code == "outgoing":


            group_name = 'DO.Approved_DO_P'
            group = self.env.ref(group_name)
            for user in group.users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',  # Activity type
                    user_id=user.id,  # Assign the activity to each user in the group
                    summary='Order is Verified P State',
                    note='The Sale_Quotation has been is set to Verified P state and is ready for review.',
                )

            group_name_2 = "DO.Verified_DO_P"
            group2 = self.env.ref(group_name_2)
            
            # Check if the current user belongs to the group2
            if self.env.user.id in group2.users.ids:
                if self.picking_type_id.is_grn_approval  == True:
                    self['approval_state']='verify'
                # elif self.picking_type_id.id in [17,20,21] :
                elif self.picking_type_id.is_rtn_approval == True:
                    self['approval_state_return']='verified'
                self['verify_by'] = self.write_uid.id
                self['verify_timestamp'] =fields.Datetime.now()

                            # Search for matching activities
                activities = self.env['mail.activity'].search([
                    ('res_model', '=', "stock.picking"),  # Related to the sale order model
                    ('res_id', '=', self.id),  # For this specific order
                    ('user_id', 'in', group2.users.ids),  # For users in the group2
                    ('summary', '=', 'Order is Prepared P State')  # Match specific activity created in action_prepared
                ])
                
                # Check if any activities are found before unlinking
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
        else:
            if self.picking_type_id.is_grn_approval  == True:
                self['approval_state']='verify'
                # elif self.picking_type_id.id in [17,20,21] :
            elif self.picking_type_id.is_rtn_approval == True:
                self['approval_state_return']='verified'
            self['verify_by'] = self.write_uid.id
            self['verify_timestamp'] =fields.Datetime.now()

    
    def action_approve(self):

        if self.picking_type_id.code == "outgoing":  # Assuming 'outgoing' indicates delivery

            group_name_2 = "DO.Approved_DO_P"
            group2 = self.env.ref(group_name_2)
            
            # Check if the current user belongs to the group2
            if self.env.user.id in group2.users.ids:
                
                if self.picking_type_id.is_grn_approval  == True:
                    self['approval_state']='approved'
                    # if self.picking_type_id.code != "outgoing":
                        # self.apply_sequence()
                    if self.picking_type_id.id == 10 and self.currency_rate:
                        self.create_landed_cost_entry()
                # elif self.picking_type_id.id in [17,20,21] :
                elif self.picking_type_id.is_rtn_approval == True:
                    self['approval_state_return']='approved'
                    # self.apply_sequence()
                
                self['Approve_by'] = self.write_uid.id
                self['approve_timestamp'] = fields.Datetime.now()




                activities = self.env['mail.activity'].search([
                        ('res_model', '=', "stock.picking"),  # Related to the sale order model
                        ('res_id', '=', self.id),  # For this specific order
                        ('user_id', 'in', group2.users.ids),  # For users in the group2
                        ('summary', '=', 'Order is Verified P State')  # Match specific activity created in action_prepared
                    ])
                    
                    # Check if any activities are found before unlinking
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
        else:
            if self.picking_type_id.is_grn_approval  == True:
                    self['approval_state']='approved'
                    # if self.picking_type_id.code != "outgoing":
                        # self.apply_sequence()
                    if self.picking_type_id.id == 10 and self.currency_rate:
                        self.create_landed_cost_entry()
                # elif self.picking_type_id.id in [17,20,21] :
            elif self.picking_type_id.is_rtn_approval == True:
                self['approval_state_return']='approved'
                # self.apply_sequence()
            
            self['Approve_by'] = self.write_uid.id
            self['approve_timestamp'] = fields.Datetime.now()




class stock_move(models.Model):
    _inherit = 'stock.move'

    reference=fields.Char('Reference',compute='_compute_reference_custom')


    def create(self, vals):
        move = super(stock_move, self).create(vals)
        # if not move.origin and move.picking_id:
        move.origin=move.picking_id.name   
        # raise UserError(str(move.read()))

        return move

    @api.depends('origin')
    def _compute_reference_custom(self):
        for rec in self:
            rec.reference=rec.origin                       
    

    


