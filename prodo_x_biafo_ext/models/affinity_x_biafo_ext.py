
from odoo import api, fields, models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, date, timedelta
from odoo.fields import Command


#Asir working for product specifications
class QualityInherit(models.Model):
    _inherit = 'quality.point'

    product_specification = fields.Html('Product Specification')

    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        for record in self:
            if record.product_ids:
                for product in record.product_ids:
                    product_id = product
                    break
                if product_id:
                    record.product_specification = product_id.product_specification if product_id.product_specification else False

class product(models.Model):
    _inherit = 'product.template'

    level_1_cat = fields.Char(string = "Product Classification", compute="split_level_of_cat",store=True)
    level_2_cat = fields.Char(string = "Product Type",compute="split_level_of_cat",store=True)
    level_3_cat = fields.Char(string = "Product Category",compute="split_level_of_cat")
    level_4_cat = fields.Char(string = "Product Group",compute="split_level_of_cat")
    level_5_cat = fields.Char(string = "Analysis 5",compute="split_level_of_cat")
    level_6_cat = fields.Char(string = "Analysis 6",compute="split_level_of_cat")
    #Asir working for product specifications
    product_specification = fields.Html('Product Specification')
    is_a_resource = fields.Boolean(string='Is A Resource', default=False)
    
    class_ = fields.Integer("Class") 
    division = fields.Integer("Division") 
    # wip_entry_account = fields.Many2one('account.account',string="WIP Entry account")
    # is_a_resource = fields.Boolean(string="Is a Resource")
    avg_price = fields.Float("Cost Price", compute="compute_avg_price",store=True,digits='Product Price'
                             ,groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders."""
                             )
    
    @api.depends('standard_price')
    def compute_avg_price(self):
        for rec in self:
            rec['avg_price'] = rec.standard_price
    
    @api.depends("categ_id")
    def split_level_of_cat(self):
        for rec in self:
            rec['level_1_cat'] = '-'
            rec['level_2_cat'] = '-'
            rec['level_3_cat'] = '-'
            rec['level_4_cat'] = '-'
            rec['level_5_cat'] = '-'
            rec['level_6_cat'] = '-'
            categ = str(rec.categ_id.complete_name)
            splited_category = categ.split("/")
           
            for i in range(len(splited_category)):
                stripeed_categry = str(splited_category[i].strip())
            
                catg_search = self.env['product.category'].search([('name','=', str(stripeed_categry))])
            
                if catg_search:
                    for catg_search_id in catg_search:
                   
                        if catg_search_id:
                            if catg_search_id.cat_level == "1":
                                
                                rec['level_1_cat'] = catg_search_id.name
                            
                                stripeed_categry = "-"
                            if catg_search_id.cat_level == "2":
                                rec['level_2_cat'] = catg_search_id.name
                                stripeed_categry = "-"
                               
                            if catg_search_id.cat_level == "3":
                                
                                rec['level_3_cat'] = catg_search_id.name
                            if catg_search_id.cat_level == '4':
                                
                                rec['level_4_cat'] = catg_search_id.name
                            if catg_search_id.cat_level == '5':
                                rec['level_5_cat'] = catg_search_id.name
                                stripeed_categry = "-"
                            if catg_search_id.cat_level == '6':
                                rec['level_6_cat'] = catg_search_id.name
                                stripeed_categry = "-"
                        else:
                            raise UserError("Category Search Loop Not Working")        
                else:
                    raise UserError("Category Search Not Working " + rec.name)
                
                

class product_category(models.Model):
    _inherit = 'product.category'

    cat_level =  fields.Char(string = "Category Level")



PURCHASE_REQUISITION_STATES = [
   ('initiated','Initiated'),
   ('store_supervisors','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
    ("cancel", "Cancel"),
    ("close_pr", "Close PR")
]

PURCHASE_REQUISITION_HEADOFFICE_STATES = [
   ('initiated','Initiated'),
   ('store_supervisors','Prepared'),
    ('checked','Checked'),
   ('verify','Verified'),

   ('reviewed','Reviewed'),
   ('approve','Approved'),
   ('cancel','Cancel') 
]


PURCHASE_REQUISITION_PLANT_STATES = [
   ('initiated','Initiated'),
   ('store_supervisors','Prepared'),
   ('recommended_by','Recommended'),
   ('checked','Checked'),
   ('verify','Verified'),
    ('reviewed','Reviewed'),
   ('approve','Approved'),
   ('cancel','Cancel')
  
]

PURCHASE_REQUISITION_MAIN_STATES = [
   ('initiated','Initiated'),
   ('store_supervisors','Prepared'),
   ('recommended_by','Recommended'),
   ('checked','Checked'),
   ('verify','Verified'),
    ('reviewed','Reviewed'),
   ('approve','Approved'),
   ('cancel','Cancel')
  
]


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    approval_state = fields.Selection(selection=PURCHASE_REQUISITION_STATES, string="Approval Status", tracking=True, required=True,
                              copy=False, default='initiated')
    main_state = fields.Selection(selection=PURCHASE_REQUISITION_MAIN_STATES, string="Status", tracking=True, required=True,readonly=True,
                              copy=False, default='initiated')
    headoffice_state = fields.Selection(selection=PURCHASE_REQUISITION_HEADOFFICE_STATES, string="Headoffice Status", tracking=True, required=True,
                              copy=False, default='initiated')
    plant_state = fields.Selection(selection=PURCHASE_REQUISITION_PLANT_STATES, string="Plant Status", tracking=True, required=True,
                              copy=False, default='initiated')
    prepared_by = fields.Many2one('res.users', string="Prepared By", readonly=True,copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    checked_by = fields.Many2one('res.users', string="Checked By", readonly=True,copy=False)
    checked_by_timestamp = fields.Datetime(strng="Checked By Timestamp" , readonly=True,copy=False)
    reviewed_by = fields.Many2one('res.users', string="Reviewed By", readonly=True,copy=False)
    reviewed_by_timestamp = fields.Datetime(strng="Reviewed By Timestamp" , readonly=True,copy=False)
    recommended_by = fields.Many2one('res.users', string="Recommended By", readonly=True,copy=False)
    recommended_by_timestamp = fields.Datetime(strng="Recommended By Timestamp" , readonly=True,copy=False)
    verify_by = fields.Many2one('res.users', string="Verified By",copy=False)
    verify_timestamp = fields.Datetime(strng="Verify Timestamp" , readonly=True,copy=False)
    approve_by = fields.Many2one('res.users', string="Approved By",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    budget_ = fields.Many2one("crossovered.budget", string='Budget')
    reject_note = fields.Text(string="Rejection Note")
    old_reference = fields.Char(string="Old Reference")
    scope_of_workboq= fields.Html(string="Scope Of Work/BOQ")
    readonly_check = fields.Boolean('Readonly Check',copy = False)
    cancel_note = fields.Text('Cancel Note')

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

    def write(self, vals):
        computed_fields = {
            name for name, field in self._fields.items() if field.compute
        }
        computed_fields.add('prepared_timestamp')
        # Check if `vals` only contains computed fields
        if set(vals.keys()).issubset(computed_fields):
            return super(PurchaseRequest, self).write(vals)
        for record in self:
            if record.approval_state == 'close_pr' and not 'approval_state' in vals.keys() and not vals.get(
                    'check_user_exists_in_group'):
                raise UserError(_("The PR is closed, you cannot edit any fields."))
            else:
                return super(PurchaseRequest, self).write(vals)

    def action_close_pr(self):
        self.approval_state = 'close_pr'


    #Asir Start
    pr_type = fields.Selection([
        ('opex', 'Opex'),
        ('capex', 'Capex')
    ], string='PR Type')

    opex_type = fields.Selection([
        ('production', 'PR - Production Material & Spares'),
        ('consumable', 'PR - Consumables & Services')
    ], string='Opex Type')

    opex_sub_type = fields.Selection([
        ('plant', 'Plant'),
        ('head_office', 'Head Office')
    ], string='Opex Sub-Type')

    capex_type = fields.Selection([
        ('plant', 'Plant'),
        ('head_office', 'Head Office')
    ], string='Capex Type')
    #Asir End
    
    def action_prepared(self):
        self['approval_state']='store_supervisors'
        self['headoffice_state']='store_supervisors'
        self['plant_state']='store_supervisors'
        self['main_state']='store_supervisors'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        # For Readonly
        self['readonly_check'] = True     

    
    def action_verify(self):
        self['approval_state'] = 'verify'
        self['headoffice_state'] = 'verify'
        self['plant_state'] = 'verify'
        self['main_state'] = 'verify'
        self['verify_by'] = self.write_uid.id
        self['verify_timestamp'] = fields.Datetime.now()
        
        # Call the button action
        self.button_to_approve()

    
    def action_approve(self):
        self['approval_state']= 'approve'
        self['headoffice_state']= 'approve'
        self['plant_state']= 'approve'
        self['main_state']= 'approve'
        self['approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self.button_approved()

      

    def action_checked(self):
       self['headoffice_state']='checked'
       self['plant_state']='checked'
       self['main_state']='checked'
       self['checked_by'] = self.write_uid.id
       self['checked_by_timestamp'] = fields.Datetime.now()
       # self.button_to_approve()  
    # from custom_budget app
       self.create_line_in_custom_budget() 

    def action_reviewed(self):
       self['headoffice_state']='reviewed'
       self['plant_state']='reviewed'
       self['main_state']='reviewed'
       self['reviewed_by'] = self.write_uid.id
       self['reviewed_by_timestamp'] = fields.Datetime.now()
       # self.button_to_approve()   

    
    def action_recommended(self):
       self['plant_state']= 'recommended_by'
       self['main_state']= 'recommended_by'
       self['recommended_by'] = self.write_uid.id
       self['recommended_by_timestamp'] = fields.Datetime.now()

    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'purchase.request',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def action_cancel(self):
       self['approval_state']= 'cancel'
       self['headoffice_state']= 'cancel'
       self['plant_state']= 'cancel'
       self['main_state']= 'cancel'       


READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

READONLY_STATES_2 = {
        'purchase': [('readonly', False)],
        'done': [('readonly', False)],
        'cancel': [('readonly', False)],
    }

PURCHASE_ORDER_STATES = [
   ('initiated','Initiated'),
   ('prepare','Prepared '),
   ('verify','Verified '),
   ('approve_cfo','Approved By CFO'),
   ('approve_coo','Approved By COO'),
   ('approve_ceo','Approved By CEO'),
]

class RequestForQuotation(models.Model):
    _inherit = "purchase.order"

    prepared_by = fields.Many2one('res.users', string="Prepared By",compute="compute_prepared_by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    approve_by = fields.Many2one('res.users', string="Approve By",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    approval_state = fields.Selection(selection=[('approve','Approve'),], string="Approval Status",copy=False, tracking=True
        )
    old_reference = fields.Char(string="Old Reference")
    
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES_2,
     change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('supplier_rank','>=',1)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    port_location = fields.Many2one('port.location', string="Port Location")
    country_origin = fields.Many2one('country.origin', string="Country of Origin")
    # purchase_order_id = fields.Many2one('purchase.order', string="Purchase ID")
    #Asir Start
    rfq_sequence = fields.Char('RFQ Ref')
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
    pr_type = fields.Selection(selection=[
        ('opex', 'Opex'),
        ('capex', 'Capex')
    ], string='PR Type')

    opex_type = fields.Selection(selection=[
        ('production', 'PR - Production Material & Spares'),
        ('consumable', 'PR - Consumables & Services')
    ], string='Opex Type')

    opex_sub_type = fields.Selection(selection=[
        ('plant', 'Plant'),
        ('head_office', 'Head Office')
    ], string='Opex Sub-Type')

    capex_type = fields.Selection(selection=[
        ('plant', 'Plant'),
        ('head_office', 'Head Office')
    ], string='Capex Type')
    #Asir End

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('compartive', 'Compartive'),
        ('comparative done', 'Comparative Done'),
        ('closed', 'Closed'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES_2, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('supplier_rank','!=', 0),('is_company','=',True)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    contract_id = fields.Many2one('contract.management',string="Contract Id")

    is_approved = fields.Boolean(string="Is Approve", default=False, readonly=True)
    
    po_attachment_ids = fields.One2many('attachment.grid','purchase_id', string="Attachment")



    #Asir overriding method of po to handle sequences on rfq on po state
    @api.model_create_multi
    def create(self, vals_list):
        orders = self.browse()
        partner_vals_list = []
        for vals in vals_list:
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
            # Ensures default picking type and currency are taken from the right company.
            self_comp = self.with_company(company_id)
            if vals.get('name', 'New') == 'New':
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                if 'state' in vals:
                    if vals['state'] == 'purchase' or vals['state'] == 'to approve':
                        vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
                    elif vals['state'] == 'draft':
                        vals['name'] = self_comp.env['ir.sequence'].next_by_code('rfq.po.state', sequence_date=seq_date) or '/'
                else:
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('rfq.po.state', sequence_date=seq_date) or '/'
            vals, partner_vals = self._write_partner_values(vals)
            partner_vals_list.append(partner_vals)
            orders |= super(RequestForQuotation, self_comp).create(vals)
        for order, partner_vals in zip(orders, partner_vals_list):
            if partner_vals:
                order.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return orders
    
    #Asir overriding method of po to handle sequences on rfq on po state
    def write(self, vals):
        if 'state' in vals:
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
            self_comp = self.with_company(company_id)
            if vals['state'] == 'purchase':
                if not self.rfq_sequence:
                    self.rfq_sequence = self.name
                    seq_date = None
                    if 'date_order' in vals:
                        seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        vals, partner_vals = self._write_partner_values(vals)
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res


    @api.depends("write_uid")
    def compute_prepared_by(self):
        for rec in self:
            rec['prepared_by'] = rec.write_uid.id
            rec['prepared_timestamp'] = fields.Datetime.now()
    
    def action_approve(self):
        self['approval_state']='approve'
        self['approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self.print_quotation()



class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line" 

    remarks = fields.Char(string="Remarks")
    opex = fields.Selection(related="request_id.opex_type", string="Opex")
    pr_type = fields.Selection(related="request_id.pr_type", string="Pr Type")
    product_type  = fields.Selection(related="product_id.detailed_type", string="Product Type")
    account_id = fields.Many2one('account.account', string="Account" , domain=[('account_type', 'in', ['expense','asset_current','asset_non_current'])] )
    price_unit = fields.Float(string='Unit Price')
    purchase_order_id = fields.Many2one('purchase.order',string="Purchase Order")
    rfq_id = fields.Many2one('purchase.order',string="RFQ")
    comparative_id = fields.Many2one('rfq.comparison',string="Comparative")
    
    # Update fields attrs 
    name = fields.Char(string="Description", tracking=True,store=True,readonly=False, compute="compute_name_and_uom")
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        tracking=True,
        domain="[('category_id', '=', product_uom_category_id)]",
        store=True,readonly=False, compute="compute_name_and_uom"
    )

    @api.depends('product_id')
    def compute_name_and_uom(self):
        for rec in self:
            rec['name'] = rec.product_id.name
            rec['product_uom_id'] = rec.product_id.uom_po_id.id
    
    @api.onchange('price_unit','product_qty')
    def onchange_product_id(self):
        for line in self:
            line['estimated_cost'] = line.price_unit * line.product_qty
        

class AccountMove(models.Model):
    _inherit='account.move'


    approval_state = fields.Selection(selection=[('prepared','Prepared'),('verified','Verified'),('approve','Approved'),], string="Approval Status",copy=False,)
    prepared_by = fields.Many2one('res.users', string="Prepared By",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    verified_by = fields.Many2one('res.users', string="Verified By",copy=False)
    verify_timestamp = fields.Datetime(strng="Verify Timestamp" , readonly=True,copy=False)
    approve_by = fields.Many2one('res.users', string="Approve By",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    old_reference = fields.Char(string="Old Reference")
    analytic_distribution = fields.Json(string="Analytic Account")
    readonly_check = fields.Boolean('Readonly Check' ,copy = False)
    # Noman
    remaining_budget = fields.Float(string="Price")
    total_knockoff = fields.Float(string="knockoff")
    # sher ahmed
    # temp_name = fields.Char(string="temp number")
    # seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)
    
    
    e_form_no = fields.Char('E-Form No')
    contrect_no = fields.Char('Contrect No')
    contrect_date = fields.Date('Contrect Date')
    # sher ahmed           

    
    
    def action_prepared(self):
        if self.move_type == "out_invoice":
            # if self.invoice_date != self.date:               
            #     raise UserError("Invoice Date Should be Equal to Document date")
            # else:
            self['approval_state']='prepared'
            self['prepared_by'] = self.write_uid.id
            self['prepared_timestamp'] = fields.Datetime.now()
        else:
            self['approval_state']='prepared'
            self['prepared_by'] = self.write_uid.id
            self['prepared_timestamp'] = fields.Datetime.now()
        
        # For Readonly
        self['readonly_check'] = True
        # sher ahmed
        # self.generate_seq()

    def action_verify(self):
        self['approval_state']='verified'
        self['verified_by'] = self.write_uid.id
        self['verify_timestamp'] = fields.Datetime.now()
    
    def action_approve(self):
        self['approval_state']='approve'
        self['approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        # sher ahmed
        # self.action_post()
    
    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.move_type in ['in_invoice','out_refund']:
                if rec['approval_state'] != "approve":
                    raise UserError(_("Required Approvals"))
                else:
                    # from custom budget app
                    # if rec.move_type == 'in_invoice':
                        # self.create_custom_budget_line_AM()
                    return res
            
    
    reject_note = fields.Text(string="Rejection Note")
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

# Rao Abdul Rehman

ACCOUNT_PAYMENT_STATES = [
   ('prepared','Prepared'),
#    ('check','Checked'),
   ('verify','Verified'),
#    ('audit','Audited'),
   ('approve','Approved'),
]

CUSTOMER_PAYMENT_STATES = [  
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
   
]
class AccountPayment(models.Model):
    _inherit = "account.payment"

    approval_state = fields.Selection(selection=ACCOUNT_PAYMENT_STATES, string="Approval Status",copy=False,)
    old_reference = fields.Char(string="Old Reference")

    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    # checked_by = fields.Many2one("res.users", string="Checked by",copy=False)
    # checked_timestamp = fields.Datetime(strng="Check Timestamp" , readonly=True,copy=False)
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    verify_timestamp = fields.Datetime(strng="Verify Timestamp" , readonly=True,copy=False)
    # audit_by = fields.Many2one("res.users", string="Audited by",copy=False)
    # audit_timestamp = fields.Datetime(strng="Audit Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # readonly_check = fields.Boolean('Readonly Check',copy = False)

    net_amount = fields.Float("Net Amount",compute="compute_net_amount")
    invoice_number = fields.Char("Invoice No")
    invoice_date = fields.Date("Invoice Date")

    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    draft_no = fields.Char(string="Draft No", compute = 'compute_draft_no')
    # sher ahmed
    temp_name = fields.Char(string="temp number")
    seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)
    
    # @api.depends("state")
    # sher ahmed
    def compute_temp_no(self):
        for rec in self:
            # raise UserError([rec.state,rec.name])
            if not rec.seq_generate:

                current_date = self.date
                current_year = current_date.year
                current_month = current_date.month
                # sequence_code = rec.journal_id.sequence_id.code
                # sequence = rec.journal_id.sequence_id.next_by_code(sequence_code, sequence_date=current_date)
   
                if rec.payment_type == 'inbound':
                    sequence_code = rec.journal_id.sequence_id_2.code
                    sequence = rec.journal_id.sequence_id_2.next_by_code(sequence_code, sequence_date=current_date)
                    
                    rec['temp_name'] = f"{rec.journal_id.customer_payment_code}-{current_year}-{current_month}-{sequence}"
                else:
                    sequence_code = rec.journal_id.sequence_id.code
                    sequence = rec.journal_id.sequence_id.next_by_code(sequence_code, sequence_date=current_date)
                    rec['temp_name'] = f"{rec.journal_id.sequence_code_short}-{current_year}-{current_month}-{sequence}"
                    
                rec['seq_generate'] = True
                self.name=self.temp_name
            else:
                if not rec.temp_name:
                    rec['temp_name'] = ""
        
    
    def compute_draft_no(self):
        for rec in self:
            rec['draft_no'] = "Draft-" + str(rec.id)
            # if rec.state == 'posted' and (not rec['name'] or rec['name'] == '/'):
                # 
    
    @api.depends("amount",)
    def compute_net_amount(self):
        for rec in self:
            rec['net_amount'] = 0
            wht_amount = 0
            for line in rec.wht_line_ids:
                wht_amount += line.amount_wht
        rec['net_amount'] = rec.amount - wht_amount
        
    def action_prepared(self):
       self['approval_state']='prepared'
       self['prepared_by'] = self.write_uid.id
       self['prepared_timestamp'] = fields.Datetime.now()
       # For Readonly
    #    self['readonly_check'] = True
       # sher ahmed
       if not self['name'] or self['name'] == "/":
           self.compute_temp_no()


    
    # def action_checked(self):
    #     self['approval_state']='check'
    #     self['checked_by'] = self.write_uid.id
    #     self['checked_timestamp'] = fields.Datetime.now()
        
    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        self['verify_timestamp'] = fields.Datetime.now()
        
    # def action_audit(self):
    #     self['approval_state']='audit'
    #     self['audit_by'] = self.write_uid.id
    #     self['audit_timestamp'] = fields.Datetime.now()
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
    
    
    # Customer Payment 
    
    approval_state_customer_payment = fields.Selection(selection=CUSTOMER_PAYMENT_STATES, string="Approval Status",copy=False,)

    prepare_customer_payment = fields.Many2one("res.users", string="Prepared",copy=False)
    prepare_customer_payment_timestamp = fields.Datetime(strng="Prepared Customer Payment Timestamp" ,copy=False, readonly=True)
    verified_customer_payment = fields.Many2one("res.users", string="Verified Customer Payment",copy=False)
    verified_customer_payment_timestamp = fields.Datetime(strng="Verified Customer Payment Timestamp" ,copy=False, readonly=True)
    approve_customer_payment = fields.Many2one("res.users", string="Approve Customer Payment",copy=False)
    approve_customer_payment_timestamp = fields.Datetime(strng="Approve  Customer Payment Timestamp" ,copy=False , readonly=True)
    
    def action_prepared_customer_payment(self):
        self['approval_state_customer_payment']='prepared'
        self['prepare_customer_payment'] = self.write_uid.id
        self['prepare_customer_payment_timestamp'] = fields.Datetime.now()
        # self['readonly_check'] = True
        # sher ahmed
        if not self['name'] or self['name'] == "/":
            self.compute_temp_no()
           
    
    def action_verify_customer_payment(self):
        self['approval_state_customer_payment']='verify'
        self['verified_customer_payment'] = self.write_uid.id
        self['verified_customer_payment_timestamp'] = fields.Datetime.now()

    def action_approve_customer_payment(self):
        self['approval_state_customer_payment']='approve'
        self['approve_customer_payment'] = self.write_uid.id
        self['approve_customer_payment_timestamp'] = fields.Datetime.now()
        
    reject_note = fields.Text(string="Rejection Note")
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.payment',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        
        
        for record in self:
            for rec in record:
                if rec.state == 'posted':
                    if rec.payment_type == 'outbound':
                        entry = self.env['account.move'].search([('ref','=',rec.name)],limit=1)
                        merge_val = {
                            'name':rec.name,
                            'journal_id': rec.journal_id.id,
                            'date':rec.date,
                            'amount':rec.amount,
                            'type':"payment",
                            'payment_id': rec.id,
                            'journal_entry':entry.id
                            
                        }
                        self.env['merging'].create(merge_val)


                if self['approval_state'] != 'approve' and self.payment_type == "outbound":
                    raise UserError(_("Required Approvals"))
                elif  self['approval_state_customer_payment'] != 'approve' and self.payment_type == "inbound":
                    raise UserError(_("Required Approvals"))
                else:
                    return res

class PartnerBank(models.Model):
    _inherit="res.partner.bank"
    
    branch_name = fields.Char("Branch Name")
 

            
#    ('check','Checked'),
#    ('verify','Verified '),
STOCK_LANDED_COST_STATES = [
   ('approve','Approved')
]
class StockLandedCost(models.Model):
    _inherit = "stock.valuation.adjustment.lines"
    
    original_value_in_unit = fields.Float(string="Original Value In Unit" , compute="computed_amount")
    new_value_in_unit = fields.Float(string="New Value In Unit" , compute="computed_amount")
    additional_landed_cost_in_unit = fields.Float(string="Additional Landed Cost In Unit" , compute="computed_amount")
    
    # @api.onchange("former_cost","final_cost","additional_landed_cost","quantity")
    def computed_amount(self):
        for rec in self:
            rec['original_value_in_unit'] = rec.former_cost/ rec.quantity
            rec['new_value_in_unit'] = rec.final_cost/ rec.quantity
            rec['additional_landed_cost_in_unit'] = rec.additional_landed_cost/ rec.quantity
            
class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"


    approval_state = fields.Selection(selection=STOCK_LANDED_COST_STATES, string="Approval Status",copy=False,)


    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False, compute='compute_prepared_by')
    checked_by = fields.Many2one("res.users", string="Checked by",copy=False)
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)


    @api.depends("write_uid")
    def compute_prepared_by(self):
        self['prepared_by'] = self.write_uid.id 
    
    def action_checked(self):
        self['approval_state']='check'
        self['checked_by'] = self.write_uid.id
        
    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
    
    def button_validate(self):
        res = super(StockLandedCost, self).button_validate()
        for rec in self:
            if rec['approval_state'] != "approve":
                raise UserError(_("Required Approvals"))
            else:
                return res



RES_PARTNER_STATES = [
   ('verify','Verified '),
   ('approve','Approved'),
]
class Partner(models.Model):
    _inherit = "res.partner"

    approval_state = fields.Selection(selection=RES_PARTNER_STATES,copy=False, string="Approval Status",)
    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False, compute='compute_prepared_by')
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)

    # commit here
    intimation_id = fields.Many2one("intimation" , string="Intimation")
    
    readonly_check = fields.Boolean('Readonly Check',copy = False)

    
    @api.depends("write_uid")
    def compute_prepared_by(self):
        self['prepared_by'] = self.create_uid.id


    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['readonly_check'] = False
    # commit here
    reject_note = fields.Text(string="Rejection Note")

    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

SALE_ORDER_STATES = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('waiting','Waiting For Approvals'),
   ('approve_coo','Approved HOD'),
   ('approve_cfo','Approved CFO'),
   ('approve_ceo','Approved CEO'),
]
SALE_ORDER2_STATES = [
   
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
   
]
READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}


# MO customization

class StockMove(models.Model):
    _inherit = "stock.move"
    product_id_2 = fields.Many2one('product.product',string='Product')
    





class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_state = fields.Selection(selection=SALE_ORDER_STATES, string="Approval Status",copy=False,)
    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    recommended_by = fields.Many2one("res.users", string="Recommended by", invisible=True,copy=False)
    recommended_by_timestamp = fields.Datetime(strng="Recommended by Timestamp" , invisible=True ,copy=False,readonly=True)
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    verify_by_timestamp = fields.Datetime(strng="Verify by Timestamp" ,copy=False, readonly=True)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_by_timestamp = fields.Datetime(strng="Approved by Timestamp",copy=False , readonly=True)
    Approve_by_cfo = fields.Many2one("res.users", string="Approved by CFO",copy=False)
    approve_by_cfo_timestamp = fields.Datetime(strng="Approved by CFO Timestamp" ,copy=False, readonly=True)
    Approve_by_ceo = fields.Many2one("res.users", string="Approved by CEO",copy=False)
    approve_by_ceo_timestamp = fields.Datetime(strng="Approved by CEO Timestamp" ,copy=False, readonly=True)
    Approve_by_coo = fields.Many2one("res.users", string="Approved by HOD",copy=False)
    approve_by_coo_timestamp = fields.Datetime(strng="Approved by HOD Timestamp" ,copy=False, readonly=True)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy = False)
    # delivery = fields.Many2one('partner_id', string='Child Partners')
    subject = fields.Html(string="Subject")

    
    prepare_sale = fields.Many2one("res.users", string="Prepared Sale",copy=False)
    prepare_sale_timestamp = fields.Datetime(strng="Prepared Sale Timestamp" ,copy=False, readonly=True)
    verified_sale = fields.Many2one("res.users", string="Verified Sale",copy=False)
    verified_sale_timestamp = fields.Datetime(strng="Verified Sale Timestamp" ,copy=False, readonly=True)
    approve_sale = fields.Many2one("res.users", string="Approve By Sale",copy=False)
    approve_sale_timestamp = fields.Datetime(strng="Approve By Sale Timestamp" ,copy=False , readonly=True)

    old_reference = fields.Char(string="Old Reference")
    ntn = fields.Char(string="NTN")
    nic = fields.Char(string="NIC")
    stn = fields.Char(string="STN")
    code = fields.Char(string="Code")

    attestation = fields.Many2one('attestation.model',string="Attestation" ,domain="[('approval_state', '!=', 'approve')]") 
    # customer_license_id = fields.Many2one('customer.license',string="Customer License")

    approval_state_sale = fields.Selection(selection=SALE_ORDER2_STATES, string="Approval Status",copy=False,)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('approval_state', '=',  'approve'),('customer_rank', '!=', 0), ('is_company','=',True)]")

    so_attachment_ids = fields.One2many('attachment.grid','sale_id', string="Attachment")

    state = fields.Selection(
        selection=[
            ('draft', "Quotation"),
            ('sent', "Quotation Approved"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    


    @api.onchange('partner_id')
    def update_info(self):
        for i in self:
            if i.partner_id.vat:
                i['ntn'] = i.partner_id.vat
            if i.partner_id.x_studio_cnic_no:
                i['nic'] = i.partner_id.x_studio_cnic_no
            if i.partner_id.x_studio_sales_tax:
                i['stn'] = i.partner_id.x_studio_sales_tax
            if i.partner_id.x_studio_new_code:
                i['code'] = i.partner_id.x_studio_new_code


    def action_revision(self):
        res = super(SaleOrder, self).action_revision()
        self['approval_state'] = False
        self['approval_state_sale'] = False
        self['prepared_by'] = False
        self['prepared_timestamp'] = False      
        self['verify_by'] = False
        self['verify_by_timestamp'] =False
        self['Approve_by'] = False
        self['approve_by_timestamp'] = False
        self['Approve_by_cfo'] = False
        self['approve_by_cfo_timestamp'] = False
        self['Approve_by_ceo'] = False
        self['approve_by_ceo_timestamp'] = False
        return res

    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True

    
    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        self['verify_by_timestamp'] = fields.Datetime.now()

    def action_approve_coo(self):
        self['approval_state']='approve_coo'
        self['Approve_by_coo'] = self.write_uid.id
        self['approve_by_coo_timestamp'] = fields.Datetime.now()
        self['state'] = 'sent'


    def send_to_cfo(self):
        self['approval_state']= 'waiting'
    
    def send_to_ceo(self):
        self['approval_state']= 'approve_coo'

    
    def action_approve_cfo(self):
        if self['approval_state'] == 'waiting':
            self['approval_state']= 'verify'
        else :
            self['approval_state']='approve_cfo'
        
        self['Approve_by_cfo'] = self.write_uid.id
        self['approve_by_cfo_timestamp'] = fields.Datetime.now()
    
    def action_approve_ceo(self):
        self['approval_state']='approve_ceo'
        self['Approve_by_ceo'] = self.write_uid.id
        self['approve_by_ceo_timestamp'] = fields.Datetime.now()
        self['state'] = 'sent'



    reject_note = fields.Text(string="Rejection Note Quotation", readonly=True)
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
        

   
    def action_prepared_sale(self):
        self['approval_state_sale']='prepared'
        self['prepare_sale'] = self.write_uid.id
        self['prepare_sale_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True

    
    
    def action_verify_sale(self):
        self['approval_state_sale']='verify'
        self['verified_sale'] = self.write_uid.id
        self['verified_sale_timestamp'] = fields.Datetime.now()

        
    def action_approve_sale(self):
        self['approval_state_sale']='approve'
        self['approve_sale'] = self.write_uid.id
        self['approve_sale_timestamp'] = fields.Datetime.now()
        self.action_confirm()

    reject_note_sale = fields.Text(string="Rejection Note Sale", readonly=True)
    
    def action_reject_sale(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        jounral_id = False  
        if self.sale_order_type == "local":            
            jounral_id = 1
        elif self.sale_order_type == "export":            
            jounral_id = 40
        else:
            jounral_id = 41
            
        res = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(self.partner_invoice_id)).id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_user_id': self.user_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [Command.set(self.transaction_ids.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            'journal_id':jounral_id
        }
        return res

    # Issuance of PO

    contract_id = fields.Many2one('contract.management',string="Contract" ,)
    implied_customer = fields.Char(string="Implied need of the Customer" ,)
    contract_attachment_id  = fields.Binary('Attachment', )
    contract_attachment_id_char = fields.Char('Attachment')

    

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    def _post_payments(self, to_process, edit_mode=False):
        res = super(AccountPaymentRegister, self)._post_payments(to_process, edit_mode=False)
        # raise UserError("s")
        """ Post the newly created payments.

        :param to_process:  A list of python dictionary, one for each payment to create, containing:
                            * create_vals:  The values used for the 'create' method.
                            * to_reconcile: The journal items to perform the reconciliation.
                            * batch:        A python dict containing everything you want about the source journal items
                                            to which a payment will be created (see '_get_batches').
        :param edit_mode:   Is the wizard in edition mode.
        """
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
        # payments.action_post()
        return res
    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.journal_id.type == "bank":
            payments = self.env['account.payment'].search([('cheque_number','=',self.cheque_number)])
            if payments:
                raise UserError("Already use this Cheque Number")
            res = {
                'date': self.payment_date,
                'amount': self.amount,
                'payment_type': self.payment_type,
                'partner_type': self.partner_type,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': self.partner_bank_id.id,
                'payment_method_line_id': self.payment_method_line_id.id,
                'destination_account_id': self.line_ids[0].account_id.id,
                'write_off_line_vals': [],
                # cheque info
                'cheque_number': self.cheque_number,
                'cheque_date': self.cheque_date,
                # 'cheque_date':self.cheque_date

            }
        else:
            payment_vals = {
                'date': self.payment_date,
                'amount': self.amount,
                'payment_type': self.payment_type,
                'partner_type': self.partner_type,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': self.partner_bank_id.id,
                'payment_method_line_id': self.payment_method_line_id.id,
                'destination_account_id': self.line_ids[0].account_id.id,
                'write_off_line_vals': [],

            }

        conversion_rate = self.env['res.currency']._get_conversion_rate(
            self.currency_id,
            self.company_id.currency_id,
            self.company_id,
            self.payment_date,
        )

        if self.payment_difference_handling == 'reconcile':

            if self.early_payment_discount_mode:
                epd_aml_values_list = []
                for aml in batch_result['lines']:
                    if aml._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
                        epd_aml_values_list.append({
                            'aml': aml,
                            'amount_currency': -aml.amount_residual_currency,
                            'balance': aml.company_currency_id.round(-aml.amount_residual_currency * conversion_rate),
                        })

                open_amount_currency = self.payment_difference * (-1 if self.payment_type == 'outbound' else 1)
                open_balance = self.company_id.currency_id.round(open_amount_currency * conversion_rate)
                early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                for aml_values_list in early_payment_values.values():
                    payment_vals['write_off_line_vals'] += aml_values_list

            elif not self.currency_id.is_zero(self.payment_difference):
                if self.payment_type == 'inbound':
                    # Receive money.
                    write_off_amount_currency = self.payment_difference
                else: # if self.payment_type == 'outbound':
                    # Send money.
                    write_off_amount_currency = -self.payment_difference

                write_off_balance = self.company_id.currency_id.round(write_off_amount_currency * conversion_rate)
                res['write_off_line_vals'].append({
                    'name': self.writeoff_label,
                    'account_id': self.writeoff_account_id.id,
                    'partner_id': self.partner_id.id,
                    'currency_id': self.currency_id.id,
                    'amount_currency': write_off_amount_currency,
                    'balance': write_off_balance,
                })
        return res
    
# Faraz Start
class PortLocation(models.Model):
    _name = "port.location"
    _description = "Port Location Model"
    
    name = fields.Char(string='Name',required=True)

class CountryOrigin(models.Model):
    _name = "country.origin"
    _description = "Country Origin Model"
    
    name = fields.Char(string='Name',required=True)

GRN_ORDER  = [
    ('prepared','Prepared P'),
    ('verify','Verified P'),
    ('approved','Approved P')
]

DISPATCH_APPROVAL  = [
    ('prepared','Prepared HO'),
    ('checked','Checked HO'),
    ('verify','Verified HO'),
    ('approved','Approved HO')
]
RETURN_ORDER  = [
    ('prepared','Prepared'),
    ('verified','Verified By HOD Inventory'),
    ('approved','Approved By PMC')
]
import json
class StockPickings(models.Model):
    _inherit = "stock.picking"

    date = fields.Date(string="Date")
    prepared_timestamp = fields.Datetime(strng="Dispatch Prepare Timestamp" , readonly=True ,copy=False)
    verify_timestamp = fields.Datetime(strng="Dispatch Timestamp" , readonly=True ,copy=False) 
    approve_timestamp = fields.Datetime(strng="Dispatch Timestamp" , readonly=True ,copy=False)
    prepared_timestamp1 = fields.Datetime(strng="Delivery Prepare Timestamp" , readonly=True ,copy=False)
    checked_timestamp1 = fields.Datetime(strng="Delivery Checked Timestamp" , readonly=True ,copy=False)
    verify_timestamp1 = fields.Datetime(strng="Delivery Verify Timestamp" , readonly=True ,copy=False) 
    approve_timestamp1 = fields.Datetime(strng="Delivery Approve Timestamp" , readonly=True ,copy=False)
    old_reference = fields.Char(string="Old Reference")
    
    returned_by = fields.Char(string='Returned By' ,copy=False)
    vehicle_no = fields.Char(string="Vehicle Registration No")
    lic_no = fields.Char(string="NOC / Lic No")
    rework = fields.Boolean(string='1. Rework (Recycle) with normal product as per approved work Instruction')
    sale = fields.Boolean(string='2. Sale as it')
    remarks = fields.Char(string='Remarks')
    gate_in_id = fields.Many2one('gate.in',string="Gate In")
    gate_in_return_id = fields.Many2one('gate.in',string="Gate In", domain="[('vendor_type' , '=' , 'sales_return')]")

    approval_state = fields.Selection(selection=GRN_ORDER, string="Approval Status",copy=False,)
    approval_state_return = fields.Selection(selection=RETURN_ORDER, string="Approval Status",copy=False,)
    
    dispatch_approval = fields.Selection(selection=DISPATCH_APPROVAL, string="Dispatch Status",copy=False,)
    # delivery_approval = fields.Selection(selection=DELIVERY_APPROVAL, string="Delivery Status",copy=False,)

    prepared_by = fields.Many2one("res.users", string="Dispatch Prepared by", compute='compute_prepared_by', readonly=True)

    prepared_by_2 =  fields.Many2one("res.users", string="Dispatch Prepared by", readonly=True)

    def action_prepare2(self):              
        if self.picking_type_id.is_grn_approval  == True:
            self['approval_state']='prepared'

        # elif self.picking_type_id.id in [17,20,21] :
        elif self.picking_type_id.is_rtn_approval == True:
            self['approval_state_return']='prepared'
            
        self['prepared_by_2'] = self.write_uid.id
        self['prepared_timestamp'] =fields.Datetime.now()
        self['readonly_check']=True

    verify_by = fields.Many2one("res.users", string="Dispatch Verify by", readonly=True)
    Approve_by = fields.Many2one("res.users", string="Dispatch Approved by", readonly=True)

    prepared_by1 = fields.Many2one("res.users", string="Delivery Prepared by", readonly=True)
    checked_by1 = fields.Many2one("res.users", string="Delivery Checked by", readonly=True)
    verify_by1 = fields.Many2one("res.users", string="Delivery Verify by", readonly=True)
    approve_by1 = fields.Many2one("res.users", string="Delivery Approved by", readonly=True)

    is_grn_approval = fields.Boolean(related="picking_type_id.is_grn_approval", string="Is GRN Approval", store=True)
    is_rtn_approval = fields.Boolean(related="picking_type_id.is_rtn_approval" ,string="Is RTN Approval", store=True)

    customer_id =fields.Many2one('res.partner',string="Customer")
    customer_code = fields.Char(string="Code" )
    customer_license_id = fields.Many2one('customer.license', string="Customer License")    
    customer_license_id_domain = fields.Char(string='Customer License Id',compute="_compute_customer_license_id_domain", readonly=True, store=False)
    
    customer_license_validity_from = fields.Date(related="customer_license_id.validity_from" ,string="Customer License Validity From")    
    customer_license_validity_to = fields.Date(related="customer_license_id.validity_to", string="Customer License Validity To")    

    name_1 =fields.Char(string="Name")
    cnic = fields.Char(string="CNIC")
    designation = fields.Char(string="Designation")
    date_1 = fields.Date(string="Date")
    intimation_id = fields.Many2one(related="partner_id.intimation_id",string="Intimation")
    #  = fields.Char(string='intimation',compute="_compute_customer_intimation_id_domain", readonly=True, store=False)
    seal_no = fields.Char(string="Seal No")
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy = False)

    driver_name = fields.Char(string='Driver Name')
    mobile_no_driver = fields.Char(string='Mobile No')
    explosive_carrier_no = fields.Char(string='Explosive Vehicle No:')
    vehicle_transport_lic_no = fields.Char(string='Vehicle Transport Licence No')
    holder_of_transport_lic_no = fields.Char(string='Customer Transport Licence No (EL-07)')
    CNIC = fields.Char(string='CNIC')
    date = fields.Date(string='Date')
    date_of_dispatched = fields.Date(string='Date of Dispatch')
    date_of_expected_arival_at_site = fields.Date(string='Date of Expected Arrival at Site')
    no_of_packags = fields.Char(string='No of Packages')
    
    current_user_group_ids = fields.Many2many(
        'res.groups',
        string='Current User Groups',
        compute='_compute_current_user_group_ids'
    )

    @api.depends('user_id')  # Assuming user_id is a field that triggers the compute
    def _compute_current_user_group_ids(self):
        for order in self:
            # Get the current user's groups
            order.current_user_group_ids = self.env.user.groups_id
    
    
    cancel_note = fields.Text('Cancel Note')

    def open_cancel_wizard(self):
        return {
            'name': _('Cancel Reason'),
            'res_model': 'cancel.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'stock.picking',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def write(self, vals):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name','=', vals.get('origin'))])
            res = super(StockPickings, self).write(vals)
            for sale in sale_order:
                if sale.sale_order_type == "local":
                    rec['picking_type_id'] = 2
                elif sale.sale_order_type == "export":
                    rec['picking_type_id'] = 36
        
            return res

    
    def _compute_customer_license_id_domain(self):
        for record in self:
            record['customer_license_id_domain'] = False
            customer_ids = []
            license = self.env['customer.license'].search([])
            for li in license:
                if li.customer_name.id not in customer_ids:   
                    customer_ids.append(li.customer_name.id)
            record.customer_license_id_domain = json.dumps([('customer_name', 'in', customer_ids)])
    

    @api.depends("write_uid")
    def compute_prepared_by(self):
        self['prepared_by'] = self.write_uid.id
    
    
    def action_prepare(self):
        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        
        if self.picking_type_id.is_grn_approval  == True:
            self['approval_state']='prepared'

        # elif self.picking_type_id.id in [17,20,21] :
        elif self.picking_type_id.is_rtn_approval == True:
            self['approval_state_return']='prepared'
            
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] =fields.Datetime.now()
        self['readonly_check']=True
        
   
    def action_verify(self):
        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        
        if self.picking_type_id.is_grn_approval  == True:
            self['approval_state']='verify'
        # elif self.picking_type_id.id in [17,20,21] :
        elif self.picking_type_id.is_rtn_approval == True:
            self['approval_state_return']='verified'
        self['verify_by'] = self.write_uid.id
        self['verify_timestamp'] =fields.Datetime.now()

    
    def action_approve(self):
        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        for rec in self:
            if rec.picking_type_id.is_grn_approval  == True:
                rec['approval_state']='approved'
                # if rec.picking_type_id.code != "outgoing":
                    # rec.apply_sequence()
                # if rec.picking_type_id.id == 10 and rec.currency_rate:
                    # rec.create_landed_cost_entry()
            # elif rec.picking_type_id.id in [17,20,21] :
            elif rec.picking_type_id.is_rtn_approval == True:
                rec['approval_state_return']='approved'
        
            
            rec['Approve_by'] = rec.write_uid.id
            rec['approve_timestamp'] = fields.Datetime.now()
        
        # self.button_validate()

    # apply sequence on Transfer (stock.picking)
    
    def apply_sequence(self):
        
        for picking in self:
            if picking.picking_type_id.is_draft_sequence:
                if picking.picking_type_id.sequence_id:
                    picking.sudo().write({
                    'name' : picking.picking_type_id.sequence_id.next_by_id()
                    })
                    picking.move_ids.reference = picking.name
                    for line in picking.move_ids:
                        line._prepare_common_svl_vals()

    def create_landed_cost_entry(self):
        # Search for the related purchase order using the origin
        po = self.env['purchase.order'].search([('name', '=', self.origin)], limit=1)

        # Search for the IQC document with picking type ID = 37 and matching origin
        sp_iqc = self.env['stock.picking'].search([('picking_type_id', '=', 37), ('origin', '=', self.origin)])

        for pick in sp_iqc:
            # Search for stock landed cost records linked to this delivery order
            slc_bill = self.env['stock.landed.cost'].search([('picking_ids', '=', self.id)])
            list_bills = []

            # Collect vendor bill IDs from landed cost records
            if slc_bill:
                for bill in slc_bill:
                    if bill.vendor_bill_id:
                        list_bills.append(bill.vendor_bill_id.id)

            # Defensive ID extraction to avoid passing 'False' strings
            po_id = po.id if po else False
            po_name = po.name if po else 'No PO Found'
            grn_id = self.id if self else False
            iqc_id = pick.id if pick else False

            # Create the landed cost approval record
            self.env['landed.cost.apporoval'].create({
                'name': po_name,
                'po_no': po_id,
                'grn_no': grn_id,
                'iqc_no': iqc_id,
                'landed_cost_attachd': [(6, 0, list_bills)]
            })


    def action_prepare1(self):
        self['dispatch_approval']='prepared'
        self['prepared_by1'] = self.write_uid.id
        self['prepared_timestamp1'] =fields.Datetime.now()
        self['readonly_check']=True
        
    def action_checked1(self):
        self['dispatch_approval']='checked'
        self['checked_by1'] = self.write_uid.id
        self['checked_timestamp1'] =fields.Datetime.now()

    def action_verify1(self):
        self['dispatch_approval']='verify'
        self['verify_by1'] = self.write_uid.id
        self['verify_timestamp1'] =fields.Datetime.now()
        
    def action_approve1(self):
        self['dispatch_approval']='approved'
        self['approve_by1'] = self.write_uid.id
        self['approve_timestamp1'] = fields.Datetime.now()
        
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
 

    reject_note = fields.Text(string="Rejection Note")
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'stock.picking',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def button_validate(self):
        pickings = super(StockPickings, self).button_validate()
        for rec in self:
            if self.picking_type_id.is_grn_approval  == True:
                if rec['approval_state'] != "approved":
                    raise UserError(_("Required Approvals"))
                else:
                    return pickings
            elif self.picking_type_id.is_rtn_approval == True:
                if rec['approval_state_return'] != "approved":
                    raise UserError(_("Required Approval"))
                else:
                    return pickings
            
        return pickings

    

class PurchaseOrderLines(models.Model):
    _inherit = "purchase.order.line"

    hs_code = fields.Many2one('hs.code', string='HS Code',related="product_id.hs_code_id")
    specification = fields.Text(string='Specification')
    product_specification = fields.Html('Product Specification')
    pr_unit_price = fields.Float(string="PR Unit Price")
    remaining_quantity = fields.Float(string="remaining Quantity")

    @api.onchange('product_id')
    def onchange_product_id_specs(self):
        for record in self:
            if record.product_id:
                if record.product_id.product_specification:
                    record.product_specification = record.product_id.product_specification

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLines, self)._prepare_account_move_line()
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        if self.account_id.id:
            res = {
                'display_type': self.display_type or 'product',
                'name': '%s: %s' % (self.order_id.name, self.name),
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'account_id':self.account_id.id,
                'quantity': self.qty_to_invoice,
                'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
                'tax_ids': [(6, 0, self.taxes_id.ids)],
                'purchase_line_id': self.id,
            }
        else:
            res = {
                'display_type': self.display_type or 'product',
                'name': '%s: %s' % (self.order_id.name, self.name),
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
                'tax_ids': [(6, 0, self.taxes_id.ids)],
                'purchase_line_id': self.id,
            }

        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution
        return res

    def _compute_price_unit_and_date_planned_and_name(self):
        res = super(PurchaseOrderLines,self)._compute_price_unit_and_date_planned_and_name()
        for line in self:
            line['name'] = line.product_id.name
        return res
   

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_on_value = fields.Float(string="Discount On Value")    
    discount_percent = fields.Float(string="Discounted Percentage")    
    
    @api.onchange('list_price','discount_percent')
    def discounted_percent(self):
        for rec in self:
            if rec.discount_percent:
                dis = rec.list_price * (rec.discount_percent/100)
                rec['price_unit'] = rec.list_price - dis
    
    @api.onchange('discount_on_value')
    def onchange_discount_percentage(self):
        for rec in self:
            if rec.discount_on_value:
                ab = (rec.discount_on_value / rec.price_subtotal) * 100
                raise UserError(ab)
    @api.depends('product_id')
    def _compute_name(self):
        res = super(SaleOrderLine,self)._compute_name()
        for line in self:
            line['name'] = line.product_id.name
        return res
    

    
class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"


    @api.model
    def create(self,vals):
        #  if 'code' in vals:
        if vals['plan_id'] == 87: 
            vals['code'] = self.env['ir.sequence'].next_by_code('pj')
        res = super(AccountAnalyticAccount,self).create(vals)
        return res
    


class Attachment(models.Model):
    _name = 'attachment.grid'

    purchase_id = fields.Many2one('purchase.order', string='Purchase order')
    sale_id = fields.Many2one('sale.order', string='Sale order')
    attachment = fields.Binary('Attachment')
    attachment_filename = fields.Char('Attachment Filename')
    attachment_comments = fields.Char('Attachment Comments')


PRODUCTION_DEMAND_PLAN = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved by COO'),
]


class ProductionDemandPlan(models.Model):
    _inherit = "production.demand.plan"


    prepare = fields.Many2one("res.users", string="Prepared" ,copy=False)
    prepare_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    verified = fields.Many2one("res.users", string="Verified",copy=False)
    verified_timestamp = fields.Datetime(strng="Verified Timestamp" ,copy=False, readonly=True)
    approve= fields.Many2one("res.users", string="Approve",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" ,copy=False, readonly=True)
    
    approval_state = fields.Selection(selection=PRODUCTION_DEMAND_PLAN, string="Approval Status",copy=False,)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check', copy=False)


    def post_action(self):
        res = super(ProductionDemandPlan, self).post_action()
        if self.approval_state == "approve":
            return res
        else:
            raise UserError('Approval Required')


    def action_prepared(self):
        for rec in self:
            for line in rec.pdo_line_id:
                if line.scheduled_date and line.product_id.produce_delay:
                    date = False 
                    if not line.urgent_requirment:
                        date = line.scheduled_date - timedelta(days= line.product_id.produce_delay)
                    else:
                        date = line.scheduled_date
                    pdo_weeks = date.isocalendar()[1] - date.replace(day=1).isocalendar()[1] + 1
                    currentdate = date.today()
                    diff = date - currentdate
                    # raise UserError(diff.day)
                    if str(diff) < "0":
                        if line.urgent_requirment != True:
                            raise UserError("Scheduled Date should not be back date")
                
                else:
                    raise UserError("Please check Product Scheduled Date or Lead Time")
        self['approval_state']='prepared'
        self['prepare'] = self.write_uid.id
        self['prepare_timestamp'] = fields.Datetime.now()
        
        self['name'] = self.env['ir.sequence'].next_by_code('pdo_seq',sequence_date=self.date)
    
    def action_verify(self):
        self['verified'] = self.write_uid.id
        self['approval_state']='verify'
        # self['verified_sale'] = self.write_uid.id
        self['verified_timestamp'] = fields.Datetime.now()

        
    def action_approve(self):
        self['approval_state']='approve'
        self['approve'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self['readonly_check']= True

        self.create_in_material_request()

    reject_note_sale = fields.Text(string="Rejection Note")
    
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'production.demand.plan',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

LNADEDCOSTAPPROVALS = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approve by COO'),
]

class LandedCostApporoval(models.Model):
    _inherit="landed.cost.apporoval"

    prepare = fields.Many2one("res.users", string="Prepared")
    prepare_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    verified = fields.Many2one("res.users", string="Verified",copy=False)
    verified_timestamp = fields.Datetime(strng="Verified Timestamp" ,copy=False, readonly=True)
    approve= fields.Many2one("res.users", string="Approve",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" ,copy=False, readonly=True)
    
    approval_state = fields.Selection(selection=LNADEDCOSTAPPROVALS, string="Approval Status",copy=False,)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy = False)



    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepare'] = self.write_uid.id
        self['prepare_timestamp'] = fields.Datetime.now()
        self['readonly_check']= True
    
    
    def action_verify(self):
        self['approval_state']='verify'
        self['verified'] = self.write_uid.id
        self['verified_timestamp'] = fields.Datetime.now()

        
    def action_approve(self):
        self['approval_state']='approve'
        self['approve'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()

    reject_note_sale = fields.Text(string="Rejection Note")


    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'landed.cost.apporoval',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }





MRP_PRODUCTION_STATES = [
   ('check','Prepared'),
   ('verify','Verified '),
   ('approve','Approved'),
]
class MRP_Production(models.Model):
    _inherit = "mrp.production"


    approval_state = fields.Selection(selection=MRP_PRODUCTION_STATES, string="Approval Status",copy=False,)
    je_posted = fields.Boolean(string='JE Posted', default=False)

    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    checked_by = fields.Many2one("res.users", string="Checked by",copy=False)
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    verify_timestamp = fields.Datetime(strng="Verify Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy=False)

    pdo_id = fields.Many2one('production.demand.plan','Production Demand Order',)
    
    
    # MO customization
    
    current_user_id = fields.Integer(
        string='Current User ID',
        default=lambda self: self.env.user.id
    )
    
    
    def action_checked(self):
        self['approval_state']='check'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        self['readonly_check']= True
        
    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        self['verify_timestamp'] = fields.Datetime.now()

        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        
        

    
    def button_mark_done(self):
        res = super(MRP_Production, self).button_mark_done()
        for rec in self:
            if rec['approval_state'] != "approve":
                raise UserError(_("Required Approvals"))
            else:
                self.create_jv_for_consumable_items()
                return res
    reject_note = fields.Text(string="Rejection Note")


    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'mrp.production',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def create_jv_for_consumable_items(self):
        for rec in self:
          if rec.state == 'done':
            if not rec.je_posted:
              for line in rec.move_raw_ids:
                getProduct = line.product_id
                if getProduct:
                  if getProduct.is_a_resource == True:
                    if line.state == 'done':
                      pamount = getProduct.standard_price * line.product_uom_qty
                      returnLines=[]
                      returnLines.append((0,0,{
                        'account_id': line.product_id.property_stock_production.valuation_out_account_id.id,
                        'name': str(rec.name) +' - '+ str(getProduct.name),
                        'currency_id': 165,
                        'debit': pamount,
                        'credit': 0.0,
                      }))
                      returnLines.append((0,0,{
                        'account_id':getProduct.property_account_expense_id.id,
                        'name': str(rec.name) +' - '+ str(getProduct.name),
                        'currency_id': 165,
                        'debit': 0.0,
                        'credit': pamount,
                      }))
                      move_id = self.env['account.move'].create({
                        'ref':str(rec.name) +' - '+ str(getProduct.name),
                        'journal_id':50,
                        'line_ids':returnLines,
                        'state':'draft'
                      })
                      if move_id:
                        move_id.action_post()


class StockPicking(models.Model):
    _inherit = "stock.move.line"

    no_of_ctn = fields.Integer("No of Carton")
    qty_in_ctn = fields.Integer("Qty In Carton")
    no_of_packages = fields.Char(string="No Of Packages",compute="compute_no_package")

    @api.depends("no_of_ctn","qty_in_ctn")
    def compute_no_package(self):
        for rec in self:
            rec['no_of_packages'] = str(rec.no_of_ctn) + ' x ' + str(rec.qty_in_ctn)
            


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    analytic_required = fields.Boolean(string='Analytic Required', compute='_compute_analytic_required')
    analytic_check = fields.Char("analytic_check" , compute="compute_analytic_check")
    
    @api.depends('account_id')
    def _compute_analytic_required(self):
        for line in self:
            line.analytic_required = line.account_id.is_analytic_required if line.account_id else False

    @api.depends("analytic_distribution",'account_id','name','debit','credit')
    def compute_analytic_check(self):
        for rec in self:
            rec['analytic_check']  = False       
            if rec.analytic_required:
                rec['analytic_check']  = rec.analytic_distribution    
            else:
                rec['analytic_check']  = 'False'    
                   

    @api.constrains('analytic_check',"analytic_distribution",'account_id','name','debit','credit','move_id.state')
    def _check_analytic_check(self):
        for line in self:
            pass
            # if line.analytic_check == False:
            #     raise ValidationError("Analytic check failed for the line with account: %s" % line.account_id.name)

# Chart of Account
ACCOUNT_ACCOUNT_STATES = [
   ('prepared','Prepared'),
   ('approve','Approved'),
]
class AccountAccount(models.Model):
    _inherit="account.account"
   
    address = fields.Char("Address")
    iban = fields.Char("IBAN")
    
    approval_state = fields.Selection(selection=ACCOUNT_ACCOUNT_STATES, string="Approval Status",copy=False,)
    
    is_analytic_required = fields.Boolean(string='Is Analytic Required')


    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy=False)
    
    reject_note = fields.Text(string="Rejection Note")

    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True

    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.account',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
PRODDUCT_TEMPLATE_STATES = [
   ('prepared','Prepared'),
   ('approve','Approved'),
]
class ProductTemplatedModel(models.Model):
    _inherit="product.template"
    
    approval_state = fields.Selection(selection=PRODDUCT_TEMPLATE_STATES, string="Approval Status",copy=False,)


    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy=False)


    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self['readonly_check']= True
    reject_note = fields.Text(string="Rejection Note")

    def action_reject(self):
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
        
        