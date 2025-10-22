from odoo import fields, models
from odoo.exceptions import UserError



class RejectionNote(models.TransientModel):
    _name = 'rejection.wizard'
    _description = 'Rejection Wizard'

    rejection_note = fields.Char(string='Rejection Note')


    def action_reject(self):
        if self['rejection_note']:
            # RIQ 
            if self._context.get('active_model') == "rqi.model":
                riq = self.env['rqi.model'].browse(
                    self._context.get('active_ids', [])
                )
                if riq:
                    if riq['reject_note']:
                        riq['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n' 
                    else:
                        riq['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n' 
                    self.riq_reject(riq)
                    return riq
            # account.account
            if self._context.get('active_model') == "account.account":
                account = self.env['account.account'].browse(
                    self._context.get('active_ids', [])
                )
                if account:
                    if account['reject_note']:
                        account['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n' 
                    else:
                        account['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n' 
                    self.account_reject(account)
                    return account
            
            # attestation.model
            if self._context.get('active_model') == "attestation.model":
                attestation = self.env['attestation.model'].browse(
                    self._context.get('active_ids', [])
                )
                if attestation:
                    if attestation['reject_note']:
                        attestation['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n' 
                    else:
                        attestation['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n' 
                    self.attestation_reject(attestation)
                    return attestation
            
            # res.partner
            if self._context.get('active_model') == "res.partner":
                partner = self.env['res.partner'].browse(
                    self._context.get('active_ids', [])
                )
                if partner:
                    if partner['reject_note']:
                        partner['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n' 
                    else:
                        partner['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n' 
                    self.partner_reject(partner)
                    return partner
           
            # product.template
            if self._context.get('active_model') == "product.template":
                template = self.env['product.template'].browse(
                    self._context.get('active_ids', [])
                )
                if template:
                    if template['reject_note']:
                        template['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n' 
                    else:
                        template['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n' 
                    self.template_reject(template)
                    return template
            # RFQ 
            if self._context.get('active_model') == "purchase.request":
                rfq = self.env['purchase.request'].browse(
                    self._context.get('active_ids', [])
                )
                if rfq:
                    if rfq['reject_note']:
                        rfq['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        rfq['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.rfq_reject(rfq)
                    return rfq
            # Account Move 
            if self._context.get('active_model') == "account.move":
                move = self.env['account.move'].browse(
                    self._context.get('active_ids', [])
                )
                if move:
                    if move['reject_note']:
                        move['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        move['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    
                    self.move_reject(move)
                    return move
            # Account Payment 
            if self._context.get('active_model') == "account.payment":
                pay = self.env['account.payment'].browse(
                    self._context.get('active_ids', [])
                )
                if pay:
                    if pay['reject_note']:
                        pay['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        pay['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.payment_reject(pay)
                    return pay
            # Stock Picking 
            if self._context.get('active_model') == "satock.picking":
                picking = self.env['stock.picking'].browse(
                    self._context.get('active_ids', [])
                )
                if picking:
                    if picking['reject_note']:
                        picking['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        picking['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.picking_reject(picking)
                    return picking
            # RFQ 
            if self._context.get('active_model') == "rfq.comparison":
                rfq = self.env['rfq.comparison'].browse(
                    self._context.get('active_ids', [])
                )
                if rfq:
                    if rfq['reject_note']:
                        rfq['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        rfq['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.rfq_com_reject(rfq)
                    return rfq
            # sale quotation
            if self._context.get('active_model') == "sale.order":
                sale = self.env['sale.order'].browse(
                    self._context.get('active_ids', [])
                )
                if sale:
                    if sale['state'] == 'draft':
                        if sale['reject_note']:
                            sale['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                        else:
                            sale['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                        self.sale_reject(sale)
                        return sale
                
                # sale order
                sale_order= self.env['sale.order'].browse(
                    self._context.get('active_ids', [])
                )
                if sale_order:
                    if sale['state'] == 'sent':
                        if sale_order['reject_note_sale']:
                            sale_order['reject_note_sale'] += ' ● '+  str(self.rejection_note)  + '\n'
                        else:
                            sale_order['reject_note_sale'] = ' ● '+  str(self.rejection_note)  + '\n'
                        self.sale_order_reject(sale_order)
                        return sale_order
            # POD
            if self._context.get('active_model') == "production.demand.plan":
                pod = self.env['production.demand.plan'].browse(
                    self._context.get('active_ids', [])
                )
                if pod:
                    if pod['reject_note']:
                        pod['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        pod['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.pod_reject(pod)
                    return pod
            # Landed Cost
            if self._context.get('active_model') == "landed.cost.apporoval":
                Lc = self.env['landed.cost.apporoval'].browse(
                    self._context.get('active_ids', [])
                )
                if Lc:
                    if Lc['reject_note']:
                        Lc['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        Lc['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.Lc_reject(Lc)
                    return Lc

            # Landed Cost
            if self._context.get('active_model') == "mrp.production":
                mrp = self.env['mrp.production'].browse(
                    self._context.get('active_ids', [])
                )
                if mrp:
                    if mrp['reject_note']:
                        mrp['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        mrp['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.mrp_reject(mrp)
                    return mrp
            
            
            if self._context.get('active_model') == "expense.module":
                expense = self.env['expense.module'].browse(
                    self._context.get('active_ids', [])
                )
                #sher ahmed
                # account_move_obj = self.env['account.move'].search([('expense_id', '=', expense.id)])
                # if account_move_obj:
                #     account_move_obj.button_cancel()
                #     account_move_obj.unlink()
                if expense.is_bank_payment == 'yes':
                    if expense['reject_note']:
                        expense['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        expense['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.bank_payment_reject(expense)
                    return expense
               
                if expense.is_bank_payment == 'no':
                    if expense['reject_note']:
                        expense['reject_note'] += ' ● '+  str(self.rejection_note)  + '\n'
                    else:
                        expense['reject_note'] = ' ● '+  str(self.rejection_note)  + '\n'
                    self.expense_reject(expense)
                    return expense


                
        else:
            raise UserError('Rejection Note Is Required')
        
    
    # Rao Abdul Rehman


    # expense Model
    
    # def bank_payment_reject(self, pay):
    #     if pay.approval_state == "prepared":
    #         pay['approval_state'] = False
    #         pay['readonly_check'] = False
    #     elif pay.approval_state == "check":
    #         pay['approval_state'] = "prepared"
    #     elif pay.approval_state == "verify":
    #         pay['approval_state'] = "check"
    #     elif pay.approval_state == "audit":
    #         pay['approval_state'] = "verify"
    #     elif pay.approval_state == "approve":
    #         pay['approval_state'] = "audit"
    
    def bank_payment_reject(self,expense):
        
            
        if expense.approval_state_expense == "prepared":
            expense['approval_state_expense'] = False
        elif expense.approval_state_expense == "verify":
            expense['approval_state_expense'] = "prepared"
        elif expense.approval_state_expense == "approve":
            expense['approval_state_expense'] = "verify"
        
        
    def expense_reject(self,expense):
        
            
        if expense.approval_state_expense == "prepared":
            expense['approval_state_expense'] = False
        elif expense.approval_state_expense == "verify":
            expense['approval_state_expense'] = "prepared"
        elif expense.approval_state_expense == "approve":
            expense['approval_state_expense'] = "verify"
            
            
    
    # RQI MODEL 
    def riq_reject(self, riq):
        if riq.state_approval == "prepare":
            riq['state_approval'] = False
    # RFQ Model 
    def rfq_reject(self, rfq):
        if (rfq.pr_type == "opex" or rfq.pr_type == "capex") and rfq.capex_type == False: 
            if rfq.approval_state == "store_supervisors":
                rfq['approval_state'] = "initiated"
                rfq['main_state'] = 'initiated'
                rfq['readonly_check'] = False

            elif rfq.approval_state == "verify":
                rfq['approval_state'] = "store_supervisors"
                rfq['main_state'] = 'store_supervisors'
                rfq.button_draft()

            elif rfq.approval_state == "approve":
                rfq['approval_state'] = "verify"
                rfq['main_state'] = 'verify'
                rfq.button_draft()

        if rfq.capex_type == "head_office": 
            if rfq.headoffice_state == "store_supervisors": 
                rfq['headoffice_state'] = "initiated"
                rfq['main_state'] = 'initiated'
                rfq['readonly_check'] = False

            elif rfq.headoffice_state == "checked": 
                rfq['headoffice_state'] = "store_supervisors"
                rfq['main_state'] = 'store_supervisors'

            elif rfq.headoffice_state == "verify": 
                rfq['headoffice_state'] = "checked"
                rfq['main_state'] = 'checked'
                rfq.button_draft()

            elif rfq.headoffice_state == "reviewed": 
                rfq['headoffice_state'] = "verify"
                rfq['main_state'] = 'verify'
                rfq.button_draft()

            elif rfq.headoffice_state == "approve": 
                rfq['headoffice_state'] = "reviewed"
                rfq['main_state'] = 'reviewed'
                rfq.button_draft()

        if rfq.capex_type == "plant":
            if rfq.plant_state == "store_supervisors": 
                rfq['plant_state'] = "initiated"
                rfq['main_state'] = "initiated"
                rfq['readonly_check'] = False 

            elif rfq.plant_state == "recommended_by": 
                rfq['plant_state'] = "store_supervisors"
                rfq['main_state'] = "store_supervisors"
                
            elif rfq.plant_state == "checked": 
                rfq['plant_state'] = "recommended_by"
                rfq['main_state'] = "recommended_by"

            elif rfq.plant_state == "verify": 
                rfq['plant_state'] = "checked"
                rfq['main_state'] = "checked"

            elif rfq.plant_state == "reviewed": 
                rfq['plant_state'] = "verify"
                rfq['main_state'] = "verify"

            elif rfq.plant_state == "approve": 
                rfq['plant_state'] = "reviewed"
                rfq['main_state'] = "reviewed"

        # sher ahmed
        if rfq.opex_sub_type == "head_office": 
            if rfq.headoffice_state == "store_supervisors": 
                rfq['headoffice_state'] = "initiated"
                rfq['main_state'] = 'initiated'
                rfq['readonly_check'] = False

            elif rfq.headoffice_state == "checked": 
                rfq['headoffice_state'] = "store_supervisors"
                rfq['main_state'] = 'store_supervisors'

            elif rfq.headoffice_state == "verify": 
                rfq['headoffice_state'] = "checked"
                rfq['main_state'] = 'checked'
                rfq.button_draft()

            elif rfq.headoffice_state == "reviewed": 
                rfq['headoffice_state'] = "verify"
                rfq['main_state'] = 'verify'
                rfq.button_draft()

            elif rfq.headoffice_state == "approve": 
                rfq['headoffice_state'] = "reviewed"
                rfq['main_state'] = 'reviewed'
                rfq.button_draft()

        if rfq.opex_sub_type == "plant":
            if rfq.plant_state == "store_supervisors": 
                rfq['plant_state'] = "initiated"
                rfq['main_state'] = "initiated"
                rfq['readonly_check'] = False 

            elif rfq.plant_state == "recommended_by": 
                rfq['plant_state'] = "store_supervisors"
                rfq['main_state'] = "store_supervisors"
                
            elif rfq.plant_state == "checked": 
                rfq['plant_state'] = "recommended_by"
                rfq['main_state'] = "recommended_by"

            elif rfq.plant_state == "verify": 
                rfq['plant_state'] = "checked"
                rfq['main_state'] = "checked"

            elif rfq.plant_state == "reviewed": 
                rfq['plant_state'] = "verify"
                rfq['main_state'] = "verify"

            elif rfq.plant_state == "approve": 
                rfq['plant_state'] = "reviewed"
                rfq['main_state'] = "reviewed"

# PURCHASE_REQUISITION_PLANT_STATES = [
#    ('initiated','Initiated'),
#    ('store_supervisors','Prepared'),
#    ('recommended_by','Recommended'),
#    ('checked','Checked'),
#    ('verify','Verifyed'),
#     ('reviewed','Reviewed'),
#    ('approve','Approved')
   
  
# ]
                # plant_state

    
    # Account Move Model
    
    def move_reject(self,move):
        if move.approval_state == "prepared":
            move['approval_state'] = False
            move['readonly_check'] = False
        elif move.approval_state == "verified":
            move['approval_state'] = "prepared"
            # move['readonly_check'] = False
        elif move.approval_state == "approve":
            move['approval_state'] = "verified"
            # move['readonly_check'] = False
            
            
    # Rao Abdul Rehman
    
    # Account Payment
    def payment_reject(self,pay):
        if pay.payment_type == "outbound":
            if pay.approval_state == "prepared":
                pay['approval_state'] = False
            elif pay.approval_state == "verify":
                pay['approval_state'] = "prepared"
            elif pay.approval_state == "approve":
                pay['approval_state'] = "verify"
    # sher ahmed
        if pay.payment_type == "inbound":
            if pay.approval_state_customer_payment == "prepared":
                # pay['readonly_check'] = False
                pay['approval_state_customer_payment'] = False
            elif pay.approval_state_customer_payment == "verify":
                pay['approval_state_customer_payment'] = "prepared"
            elif pay.approval_state_customer_payment == "verify":
                pay['approval_state_customer_payment'] = "approve"
            
                
    

    def picking_reject(self,picking):
        if picking.picking_type_id.id in [1,10,11,16]:
            picking['approval_state']=False
            picking['readonly_check'] = False
        elif picking.picking_type_id.id in [17,20,21] :
            if picking.approval_state_return == 'prepared':
                picking['approval_state_return']=False
            elif picking.approval_state_return == 'verified':
                picking['approval_state_return']='prepared'


        picking['Approve_by'] = picking.write_uid.id
            


    def rfq_com_reject(self,rfq):
        if rfq.po_approval_state == "prepare":
            rfq['po_approval_state'] = "initiated"
            rfq['readonly_check'] = False
        elif rfq.po_approval_state == "verify":
            rfq['po_approval_state'] = "prepare"
        elif rfq.po_approval_state == "approve_cfo":
            rfq['po_approval_state'] = "verify"
        elif rfq.po_approval_state == "approve_coo":
            rfq['po_approval_state'] = "approve_cfo"


    # Sale Quotation
    def sale_reject(self, sale):
        if sale['approval_state'] == "prepared":
            sale['approval_state'] = False
            sale['readonly_check'] = False
            
        elif sale['approval_state'] == "verify":
            sale['approval_state'] = "prepared"
            sale['sent_to_ceo'] = True
            sale['sent_to_cfo'] = True
            
        elif sale['approval_state'] in ["approve_coo", "waiting", 'approve_cfo', 'approve_ceo']:
            sale['approval_state'] = "verify"
            sale['approved_cfo'] = False
            sale['sent_to_ceo'] = False
            sale['sent_to_cfo'] = False

        elif sale['approval_state'] in ['approve_cfo', 'approve_ceo']:
            sale['approval_state'] = "verify"
            sale['approved_cfo'] = False
            sale['sent_to_ceo'] = False
            sale['sent_to_cfo'] = False


    


    # sale order   
    def sale_order_reject(self,sale):
        # raise UserError("s")
        if sale.approval_state_sale == "prepared":
            sale['approval_state_sale'] = False
            sale['readonly_check'] = False
        elif sale.approval_state_sale == "verify":
            sale['approval_state_sale'] = "prepared"
        elif sale.approval_state_sale == "approve":
            sale['approval_state_sale'] = "verify"
      
   
    # POD
    def pod_reject(self,sale):
        if sale.approval_state == "prepared":
            sale['approval_state'] = False
        elif sale.approval_state == "verify":
            sale['approval_state'] = "prepared"
        elif sale.approval_state == "approve":
            sale['approval_state'] = "verify"
            sale['readonly_check'] = False

    # PDO
    def pod_reject(self,pdo):
        
        if pdo.approval_state == "verify":
            pdo['approval_state'] = "prepared"
        elif pdo.approval_state == "approve":
            pdo['approval_state'] = "verify"
            pdo['approval_state'] = False
    
    # Landed Cost
    def Lc_reject(self,lc):
        if lc.approval_state == "prepared":
            lc['approval_state'] = False
            lc['readonly_check'] = False
        elif lc.approval_state == "verify":
            lc['approval_state'] = "prepared"
        elif lc.approval_state == "approve":
            lc['approval_state'] = "verify"


    def mrp_reject(self,mrp):
        if mrp.approval_state == "check":
            mrp['approval_state'] = False
            mrp['readonly_check'] = False
        elif mrp.approval_state == "verify":
            mrp['approval_state'] = "check"
        elif mrp.approval_state == "approve":
            mrp['approval_state'] = "verify"
    
    # def partner_reject(self,partner):
    #     if partner.approval_state == "approve":
    #         partner['approval_state'] = "verify"
    #         partner['readonly_check'] = False
        

    # def account_reject(self,account):
    #     if account.approval_state == "approve":
    #         account['approval_state'] = "prepared"
    #         account['readonly_check'] = False
    
    # def attestation_reject(self,account):
    #     if account.approval_state == "approve":
    #         account['approval_state'] = "prepared"
    #         account['readonly_check'] = False
    
    
    # def template_reject(self,template):
    #     if template.approval_state == "approve":
    #         template['approval_state'] = "prepared"
    #         template['readonly_check'] = False
    

    def partner_reject(self,partner):
        if partner.approval_state == "verify":
            partner['approval_state'] = False
        if partner.approval_state == "approve":
            partner['approval_state'] = "verify"
        partner['readonly_check'] = False
        if  partner['active']:
            partner['active'] = False
        if partner['is_published']:
            partner['is_published'] = False
        

    def account_reject(self,account):
        if account.approval_state == "prepared":
            raise UserError('Record is not Approved yet!')
        # raise UserError('Hello!!! account')
        if account.approval_state == "approve":
            account['approval_state'] = "prepared"
            account['readonly_check'] = False
            if not account['deprecated']:
                account['deprecated'] = True
            if account['is_published']:
                account['is_published'] = False
        

    
    def attestation_reject(self,account):
        if account.approval_state == "approve":
            account['approval_state'] = "prepared"
            account['readonly_check'] = False
    
    
    def template_reject(self,template):
        if template.approval_state == "prepared":
            raise UserError('Record is not Approved yet!')
        # raise UserError('Hello!!! product')
        if template.approval_state == "approve":
            template['approval_state'] = "prepared"
            template['readonly_check'] = False
            if  template['active']:
                template['active'] = False
            if template['is_published']:
                template['is_published'] = False
