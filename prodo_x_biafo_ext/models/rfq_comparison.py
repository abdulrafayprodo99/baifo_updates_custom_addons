from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime
import json
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def create_rfq_comparisons(self):
            # for record in self:
            #     if not record.approval_state == "approve":
            #         # raise UserError('Approval Required')
            pr_names = []
            pr_detail_list = []
            po_detail_list = []
            calc_detail_mapping = []
            calc_detail_list = []
            vendor_detail_list = []
            pr_ids_list = []
            rfq_comp_name = ''

            #working for comparison name
            for record in self:
                if record.purchase_request_id:
                    if record.purchase_request_id.id not in pr_ids_list:
                        pr_names.append(record.purchase_request_id.name)
                        pr_ids_list.append(record.purchase_request_id.id)
            rfq_comp_name = rfq_comp_name.join(pr_names) + ' Comparison'

            #working for purchase request details
            pr_ids = self.env['purchase.request'].search([('id','in',pr_ids_list)])
            if pr_ids:
                for pr in pr_ids:
                    for line in pr.line_ids:
                        pr_detail_list.append((0,0,{
                            'purchase_request_id': pr.id,
                            'product_code':line.product_id.product_tmpl_id.default_code,
                            'product_id':line.product_id.id,
                            'product_specification':line.product_id.product_tmpl_id.product_specification if line.product_id.product_tmpl_id.product_specification else False,
                            'product_qty':line.product_qty,
                            'product_uom_id':line.product_uom_id.id,
                        }))
            
            #working for purchase order details
            for record in self:
                for line in record.order_line:
                    po_detail_list.append((0,0,{
                        'purchase_order_id': record.id,
                        'currency_id': record.currency_id.id,
                        'product_code':line.product_id.product_tmpl_id.default_code,
                        'product_id':line.product_id.id,
                        'product_qty':line.product_qty,
                        'account_id': line.account_id.id,
                        'specifications': line.specification,
                        'product_uom_id':line.product_uom.id,
                        'product_unit_price': line.price_unit,
                        'partner_id': record.partner_id.id,
                        'payment_term_id': record.payment_term_id.id if record.payment_term_id else False,
                        'tax_ids': line.taxes_id.ids if line.taxes_id else False,
                    }))

            #create rfq comparison record
            rfq_rec = self.env['rfq.comparison'].create({
                'name': rfq_comp_name,
                'purchase_request_id': pr_ids_list[0],
                'pr_detail_ids': pr_detail_list,
                'po_detail_ids': po_detail_list,
            })

            #working for calculations
            if rfq_rec:
                # <Bilal Start Here>
                for rec in self:
                    rec.write({
                        'state':"compartive"
                    })
                # <Bilal END Here>
                for rfq in rfq_rec:
                    for po_detail in rfq.po_detail_ids:
                        if not calc_detail_mapping:
                            obj = {
                                'product_id': po_detail.product_id.id,
                                'currency_id': po_detail.currency_id.id,
                                'product_code': po_detail.product_id.product_tmpl_id.default_code,
                                'min_check': po_detail.product_unit_price,
                                'max_check': po_detail.product_unit_price,
                                'account_id': po_detail.account_id.id,
                                'specifications': po_detail.specifications,
                            }
                            calc_detail_mapping.append(obj.copy())
                        else:
                            operation_done = False
                            
                            for calc_detail in calc_detail_mapping:
                                
                                if calc_detail['specifications']:
                                    if calc_detail['product_id'] == po_detail.product_id.id and calc_detail['specifications'] == po_detail.specifications:
                                        operation_done = True
                                        if po_detail.product_unit_price < calc_detail['min_check']:
                                            calc_detail['min_check'] = po_detail.product_unit_price
                                        if po_detail.product_unit_price > calc_detail['max_check']:
                                            calc_detail['max_check'] = po_detail.product_unit_price
                                else:
                                    if calc_detail['product_id'] == po_detail.product_id.id: 
                                        operation_done = True
                                        if po_detail.product_unit_price < calc_detail['min_check']:
                                            calc_detail['min_check'] = po_detail.product_unit_price
                                        if po_detail.product_unit_price > calc_detail['max_check']:
                                            calc_detail['max_check'] = po_detail.product_unit_price
                            if not operation_done:
                                obj = {
                                    'product_id': po_detail.product_id.id,
                                    'currency_id': po_detail.currency_id.id,
                                    'product_code': po_detail.product_id.product_tmpl_id.default_code,
                                    'min_check': po_detail.product_unit_price,
                                    'max_check': po_detail.product_unit_price,
                                    'account_id': po_detail.account_id.id,
                                    'specifications': po_detail.specifications,
                                }
                                calc_detail_mapping.append(obj.copy())

                # raise UserError(str(calc_detail_mapping))
                if calc_detail_mapping:
                    # raise UserError(str(calc_detail_mapping))
                    for calc_detail in calc_detail_mapping:
                        calc_detail_list.append((0,0,{
                            'product_code':calc_detail['product_code'],
                            'currency_id':calc_detail['currency_id'],
                            'product_id':calc_detail['product_id'],
                            'min_check':calc_detail['min_check'],
                            'max_check':calc_detail['max_check'],
                           
                        }))
                    
                    rfq_rec.write({
                        'calculation_ids': calc_detail_list,
                    })
            
                    #working for vendor selections
                    for calc_detail in calc_detail_mapping:
                        vendor_detail_list.append((0,0,{
                            'product_code':calc_detail['product_code'],
                            'currency_id':calc_detail['currency_id'],
                            'product_id':calc_detail['product_id'],
                            'account_id':calc_detail['account_id'],
                            'specifications':calc_detail['specifications'],

                        }))
                    
                    # raise UserError(str(calc_detail_mapping))
                    rfq_rec.write({
                        'vendor_selection_ids': vendor_detail_list,
                    })
# bilal start        
PURCHASE_ORDER_STATES = [
   ('initiated','Initiated'),
   ('prepare','Prepared '),
   ('verify','Checked '),
   ('approve_cfo','Verified By CFO'),
   ('approve_coo','Verified By COO'),
   ('approve_ceo','Approved By CEO'),
]
# bilal End        
class RfqComparison(models.Model):
    _name = 'rfq.comparison'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
    pr_detail_ids = fields.One2many('rfq.comparison.pr.detail', 'rfq_comparison_id', string='PR Details')
    po_detail_ids = fields.One2many('rfq.comparison.po.detail', 'rfq_comparison_id', string='PO Details')
    attachment_ids = fields.One2many('rfq.comparison.attachment', 'rfq_comparison_id', string='Attachments')
    calculation_ids = fields.One2many('rfq.comparison.calculation', 'rfq_comparison_id', string='Calculations')
    vendor_selection_ids = fields.One2many('rfq.comparison.vendor.selection', 'rfq_comparison_id', string='Vendor Selection')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'POs Generated')
    ], string='Status', default='draft')
    total_incl_tax = fields.Float('Total With Tax', compute="_compute_total_incl_tax")
    total_excl_tax = fields.Float('Total Without Tax', compute="_compute_total_excl_tax")
    total_tax = fields.Float('Total Tax', compute="_compute_total_tax")

    @api.depends('total_incl_tax','total_excl_tax')
    def _compute_total_tax(self):
        for record in self:
            record.total_tax = record.total_incl_tax - record.total_excl_tax

    @api.depends('vendor_selection_ids.product_subtotal')
    def _compute_total_excl_tax(self):
        for record in self:
            amt = 0
            for line in record.vendor_selection_ids:
                amt += line.product_subtotal
            record['total_excl_tax'] = amt

    @api.depends('vendor_selection_ids.product_subtotal_incl_tax')
    def _compute_total_incl_tax(self):
        for record in self:
            amt = 0
            for line in record.vendor_selection_ids:
                amt += line.product_subtotal_incl_tax
            record.total_incl_tax = amt

    # bilal Start
    po_approval_state = fields.Selection(selection=PURCHASE_ORDER_STATES, string="Approval Status", tracking=True,
                              copy=False, default="initiated")

    prepared_by = fields.Many2one('res.users', string="Prepared By",readonly=True,copy=False)
    prepared_timestamp = fields.Datetime(string="Prepared Timestamp",readonly=True,copy=False)
    verified_by = fields.Many2one('res.users', string="Verified By",readonly=True,copy=False)
    verified_timestamp = fields.Datetime(string="Verified Timestamp",readonly=True,copy=False)
    approve_by_cfo = fields.Many2one('res.users', string="Approve By CFO",readonly=True,copy=False)
    approve_by_cfo_timestamp = fields.Datetime(string="Approve By CFO Timestamp",readonly=True,copy=False)
    approve_by_coo = fields.Many2one('res.users', string="Approve By COO",readonly=True,copy=False)
    approve_by_coo_timestamp = fields.Datetime(string="Approve By COO Timestamp",readonly=True,copy=False)
    approve_by_ceo = fields.Many2one('res.users', string="Approve By CEO",readonly=True,copy=False)
    approve_by_ceo_timestamp = fields.Datetime(string="Approve By CEO Timestamp",readonly=True,copy=False)
    product_id_domain = fields.Char(string='Product Domain',compute="_compute_product_id_domain", readonly=True, store=False)
    partner_id_domain = fields.Char(string='Supplier Domain',compute="_compute_partner_id_domain", readonly=True, store=False)
    remarks = fields.Text('Remarks')
    # bilal start
    auto_fill_supplier = fields.Boolean(string="Auto Fill Supplier")
    # bilal end
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy = False)


    # bilal Start
    @api.onchange('auto_fill_supplier')
    def auto_fill_supplier_on_vendor_line(self):
        # raise UserError("s")
        for rec in self:
            # min_price_suppliers_dict = []
            min_price_suppliers = defaultdict(lambda: {'product_unit_price': float('inf'), 'partner_id': None})
            if rec.auto_fill_supplier == True:
                for entry in rec.po_detail_ids:
                    product_id = entry['product_id']
                    price = entry['product_unit_price']

                    if price < min_price_suppliers[product_id]['product_unit_price']:
                        min_price_suppliers[product_id] = {'product_unit_price': price, 'partner_id': entry['partner_id']}

                min_price_suppliers_dict = dict(min_price_suppliers)
                # raise UserError("saaa")
                # raise UserError(str(min_price_suppliers_dict))
                for line in rec.vendor_selection_ids:
                    for key, items in min_price_suppliers_dict.items():
                        if line.product_id.id == key.id:
                            line['partner_id'] = min_price_suppliers_dict[key]['partner_id'].id
                            line._onchange_partner_id()
    # bilal End 



    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('rfq.comparison.sequence')
        return super().create(vals)

    def _compute_partner_id_domain(self):
        for record in self:
            record.partner_id_domain = False
            vendor_ids = []
            for line in record.po_detail_ids:
                if line.partner_id.id not in vendor_ids:
                    vendor_ids.append(line.partner_id.id)
            if vendor_ids:
                record.partner_id_domain = json.dumps([('id', 'in', vendor_ids)])

    def _compute_product_id_domain(self):
        for record in self:
            record['product_id_domain'] = False
            product_ids = []
            for line in record.po_detail_ids:
                if line.product_id.id not in product_ids:
                    product_ids.append(line.product_id.id)
                record.product_id_domain = json.dumps([('id', 'in', product_ids)])

        
    def action_prepared(self):
        self['po_approval_state']='prepare'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        self['readonly_check']=True
    
    def action_verified(self):
        self['po_approval_state']='verify'
        self['verified_by'] = self.write_uid.id
        self['verified_timestamp'] = fields.Datetime.now()
    
    def action_approve_by_cfo(self):
        self['po_approval_state']='approve_cfo'
        self['approve_by_cfo'] = self.write_uid.id
        self['approve_by_cfo_timestamp'] = fields.Datetime.now()
    
    def action_approve_coo(self):
        self['po_approval_state']='approve_coo'
        self['approve_by_coo'] = self.write_uid.id
        self['approve_by_coo_timestamp'] = fields.Datetime.now()
    
    def action_approve_by_ceo(self):
        self['po_approval_state']='approve_ceo'
        self['approve_by_ceo'] = self.write_uid.id
        self['approve_by_ceo_timestamp'] = fields.Datetime.now()

    # def action_reject(self):
    #     if self.po_approval_state == "prepare":
    #         self['po_approval_state'] = "initiated"
    #     elif self.po_approval_state == "verify":
    #         self['po_approval_state'] = "prepare"
    #     elif self.po_approval_state == "approve_cfo":
    #         self['po_approval_state'] = "verify"
    #     elif self.po_approval_state == "approve_coo":
    #         self['po_approval_state'] = "approve_cfo"
    

    reject_note = fields.Text(string="Rejection Note")
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'rfq.comparison',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    

    # bilal End


    def generate_rfqs(self):
        for record in self:
            if record.po_approval_state == "approve_ceo":
                valid_comparison = True
                if record.vendor_selection_ids:
                    for line in record.vendor_selection_ids:
                        if not line.partner_id:
                            valid_comparison = False
                else:
                    valid_comparison = False
                
                if not valid_comparison:
                    raise UserError('Please fill the vendor selection details')
                else:
                    #generate rfq
                    vendor_ids = []
                    for line in record.vendor_selection_ids:
                        if line.partner_id.id not in vendor_ids:
                            vendor_ids.append(line.partner_id.id)

                    if vendor_ids:
                        for vendor_id in vendor_ids:
                            po_line_data = []
                            rfq_name = ''
                            vendor_line_ids = record.vendor_selection_ids.filtered(lambda vendor_line_id: vendor_line_id.partner_id.id == vendor_id)
                            po_line_ids = record.po_detail_ids.filtered(lambda po_line_id: po_line_id.partner_id.id == vendor_id)
                            if po_line_ids:
                                for po_line in po_line_ids:
                                    rfq_name = po_line.purchase_order_id.name
                                   
                                    break

                            pterm_id = 0
                            for vendor_line in vendor_line_ids:
                                pterm_id = vendor_line.payment_term_id.id if vendor_line.payment_term_id else 0
                                break

                            if vendor_line_ids:
                                for vendor_line in vendor_line_ids:
                                    po_line_data.append((0,0,{
                                        'product_id':vendor_line.product_id.id,
                                        'account_id':vendor_line.account_id.id,
                                        'specification':vendor_line.specifications,
                                        'product_specification': vendor_line.product_id.product_tmpl_id.product_specification,
                                        'date_planned': datetime.now(),
                                        'product_qty':vendor_line.product_qty,
                                        'product_uom':vendor_line.product_uom_id.id,
                                        'price_unit':vendor_line.product_unit_price,
                                        'taxes_id':vendor_line.tax_ids.ids,
                                    }))
                                # Noman
                                order_ids = []
                                picking_type_ids = []
                                delivery_address = []
                                detail = []
                                for vendor_li in vendor_line_ids:
                                    purchase = self.env['purchase.order'].search([('purchase_request_id','=',record.purchase_request_id.id),('partner_id','=',vendor_li.partner_id.id)])
                                    for pur in purchase:
                                        if pur:
                                            order_ids.append(pur.currency_id.id)
                                            picking_type_ids.append(pur.picking_type_id.id)
                                            delivery_address.append(pur.x_studio_delivery_address.id)
                                            
                                            detail.append({
                                                "country_origin": pur.country_origin.id,
                                                "incoterm_id": pur.incoterm_id.id,
                                                "incoterm_location":pur.incoterm_location,
                                                "port_location":pur.port_location.id
                                            })            
                                
                                # Noman
                                created_po = self.env['purchase.order'].create({
                                    'state': 'to approve',
                                    'partner_id': vendor_id, 
                                    'date_planned': datetime.now(),
                                    'purchase_request_id': record.purchase_request_id.id if record.purchase_request_id else False,
                                    'pr_type': record.purchase_request_id.pr_type if record.purchase_request_id.pr_type else False,
                                    'opex_type': record.purchase_request_id.opex_type if record.purchase_request_id.opex_type else False,
                                    'opex_sub_type': record.purchase_request_id.opex_sub_type if record.purchase_request_id.opex_sub_type else False,
                                    'capex_type': record.purchase_request_id.capex_type if record.purchase_request_id.capex_type else False,
                                    'order_line': po_line_data, 
                                    'rfq_sequence': rfq_name, 
                                    'currency_id': order_ids[0] if order_ids else False, 
                                    'x_studio_delivery_address' : delivery_address[0] if delivery_address else False,
                                    'picking_type_id': picking_type_ids[0] if picking_type_ids else False, 
                                    'payment_term_id': pterm_id if pterm_id != 0 else False, 
                                    
                                    "country_origin": detail[0]['country_origin'] if detail else False,
                                    "incoterm_id": detail[0]['incoterm_id'] if detail else False,
                                    "incoterm_location":detail[0]['incoterm_location'] if detail else False,
                                    "port_location":detail[0]['port_location'] if detail else False,
                                })
                                # raise UserError("hello")
                                if created_po:
                                    for field_name, field in created_po._fields.items():
                                        #raise UserError(str(field_name))
                                        field.readonly = True
                                    # bilal start
                                    for po_line in record.po_detail_ids:
                                        po_line.purchase_order_id.state = "comparative done"
                                        # po_line.purchase_order_id.button_done()
                                    # bilal end
                    #update the status
                    record.write({
                        'state': 'done',
                    })

            else:
                raise UserError("Approval Required")

class RfqComparisonPrDetail(models.Model):
    _name = 'rfq.comparison.pr.detail'

    product_code = fields.Char('Product Code')
    product_id = fields.Many2one('product.product', string='Product')
    product_specification = fields.Html('Product Spec')
    product_qty = fields.Float('Qty')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
    rfq_comparison_id = fields.Many2one('rfq.comparison', string='RFQ Comparison')

    remarks = fields.Char(string="Remarks")

class RfqComparisonAttachment(models.Model):
    _name = 'rfq.comparison.attachment'

    rfq_comparison_id = fields.Many2one('rfq.comparison', string='RFQ Comparison')
    attachment = fields.Binary('Attachment')
    attachment_filename = fields.Char('Attachment Filename')
    attachment_comments = fields.Char('Attachment Comments')

class RfqComparisonPoDetail(models.Model):
    _name = 'rfq.comparison.po.detail'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    product_code = fields.Char('Product Code')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float('Qty')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    product_unit_price = fields.Float(string='Unit Price')
    product_subtotal = fields.Monetary(compute='_compute_product_subtotal', string='Subtotal W/O Tax', store=True)
    product_subtotal_incl_tax = fields.Monetary(compute='_compute_product_subtotal_incl_tax', string='Subtotal W Tax', store=True)
    rfq_comparison_id = fields.Many2one('rfq.comparison', string='RFQ Comparison')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    remarks = fields.Char(string="Remarks")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)

    # 
    account_id = fields.Many2one('account.account',string="Account")
    specifications = fields.Text()

    # 
    @api.depends('product_qty','product_unit_price')
    def _compute_product_subtotal(self):
        for record in self:
            record.product_subtotal = record.product_unit_price * record.product_qty

    @api.depends('product_qty','product_unit_price','tax_ids')
    def _compute_product_subtotal_incl_tax(self):
        for record in self:
            tax_amount = 0
            if record.tax_ids:
                for tax in record.tax_ids:
                    tax_amount = tax_amount + (record.product_unit_price * (tax.amount/100))
            subtotal_incl_tax = record.product_unit_price + tax_amount
            record.product_subtotal_incl_tax = subtotal_incl_tax * record.product_qty 

class RfqComparisonCalculation(models.Model):
    _name = 'rfq.comparison.calculation'

    rfq_comparison_id = fields.Many2one('rfq.comparison', string='RFQ Comparison')
    product_code = fields.Char('Product Code')
    product_id = fields.Many2one('product.product', string='Product')
    min_check = fields.Monetary('Minimum Check')
    max_check = fields.Monetary('Maximum Check')
    difference_amount = fields.Monetary(compute='_compute_difference_amount', string='Difference', store=True)
    difference_perc = fields.Float(compute='_compute_difference_perc', string='Difference (%)', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)

    remarks = fields.Char(string="Remarks")

    @api.depends('min_check','max_check')
    def _compute_difference_amount(self):
        for record in self:
            record.difference_amount = record.max_check - record.min_check

    @api.depends('min_check','difference_amount')
    def _compute_difference_perc(self):
        for record in self:
            if record.min_check > 0:
                record.difference_perc = (record.difference_amount / record.min_check) * 100
            else:
                record.difference_perc = 0

class RfqComparisonVendorSelection(models.Model):
    _name = 'rfq.comparison.vendor.selection'

    rfq_comparison_id = fields.Many2one('rfq.comparison', string='RFQ Comparison')
    product_code = fields.Char('Product Code')
    product_id = fields.Many2one('product.product', string='Product')
  
    product_subtotal = fields.Monetary(compute='_compute_product_subtotal', string='Subtotal W/O Tax', store=True)
    product_subtotal_incl_tax = fields.Monetary(compute='_compute_product_subtotal_incl_tax', string='Subtotal W Tax', store=True)
    product_unit_price = fields.Float(string='Unit Price')
    product_qty = fields.Float(string='Qty')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    product_id_domain = fields.Char('Product Domain', related='rfq_comparison_id.product_id_domain')
    partner_id_domain = fields.Char('Supplier Domain', related='rfq_comparison_id.partner_id_domain')
    tax_ids = fields.Many2many('account.tax', string='Tax')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    remarks = fields.Char(string="Remarks")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)

    # bilal start
    account_id = fields.Many2one('account.account', string="Account")
    specifications = fields.Text()

    # bilal End

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.product_code = record.product_id.product_tmpl_id.default_code

    @api.depends('product_qty','product_unit_price')
    def _compute_product_subtotal(self):
        for record in self:
            record.product_subtotal = record.product_unit_price * record.product_qty

    @api.depends('product_qty','product_unit_price','tax_ids')
    def _compute_product_subtotal_incl_tax(self):
        for record in self:
            tax_amount = 0
            if record.tax_ids:
                for tax in record.tax_ids:
                    tax_amount = tax_amount + (record.product_unit_price * (tax.amount/100))
            subtotal_incl_tax = record.product_unit_price + tax_amount
            record.product_subtotal_incl_tax = subtotal_incl_tax * record.product_qty
            
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for record in self:
            if record.partner_id:
                po_line_ids = record.rfq_comparison_id.po_detail_ids.filtered(
                    lambda po_line_id: (po_line_id.product_id.id == record.product_id.id and 
                                        po_line_id.partner_id.id == record.partner_id.id) and 
                                        po_line_id['specifications'] == record.specifications
                )

                if po_line_ids:
                    for po_line_id in po_line_ids:
                        record.product_unit_price = po_line_id.product_unit_price
                        record.product_qty = po_line_id.product_qty
                        record.product_uom_id = po_line_id.product_uom_id.id
                        record.tax_ids = po_line_id.tax_ids.ids if po_line_id.tax_ids else False
                        record.payment_term_id = po_line_id.payment_term_id.id if po_line_id.payment_term_id else False
                        break
                else:
                    # Log the issue and continue
                    _logger.warning('Selected supplier is not valid for product: %s', record.product_id.name)
                    record.product_unit_price = 0
                    record.product_qty = 0
                    record.product_uom_id = False
                    record.tax_ids = False
                    record.payment_term_id = False






    