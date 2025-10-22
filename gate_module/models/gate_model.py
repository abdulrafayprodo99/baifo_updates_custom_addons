# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class GateINModule(models.Model):
    _name = "gate.in"
    _description = "Gate Module"

    name = fields.Char(string='Gate Reference', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    vendor_type = fields.Selection([('vendor', 'Vendor'),('seles_return','Sales Return'), ('other', 'Other')], string='Gate In Vendor Type' ,required=True,)
    gate_type = fields.Selection([('returnable', 'Returnable'), ('nonreturnable', 'Non Returnable')], string='Gate In Type', required=True,)
    partner_id = fields.Many2one('res.partner',string='Partner')
    vendor_name= fields.Char(string='Vendor')
    purchase_id = fields.Many2one('purchase.order',string='Purchase Order')
    return_date = fields.Date(string='Return Date',)
    line_id = fields.One2many('gate.vendor.line', 'gate_module_id', string="Gate Line")
    line_ids = fields.One2many('gate.other.line', 'gate_module_id', string="Gate Line")
    return_line_ids = fields.One2many('gate.return.line', 'gate_module_id', string="Gate Return Line")
    location_name = fields.Selection([('facorty', 'Facorty'),('ho', 'Head Office')],string="Location Name")
    receiver_name = fields.Char(string="Receiver Name")
    department = fields.Char(string="Department")
    department_id = fields.Many2one('stock.location' , string="Department")
    attention_to = fields.Char(string="Attention To")
    date_time = fields.Datetime(string="Date Time")
    saneder_name = fields.Char(string="Sender Name")
    saneder_number= fields.Char(string="Sender Number")
    vehicle_number= fields.Char(string="Vehicle Number")
    phone  = fields.Binary(string="Photo")
    bilty_number = fields.Char(string="Bilty Number")
    delivery_challan_number = fields.Many2one('stock.picking',string="Delivery Challan Number")

    state = fields.Selection([('draft', "Draft"),('done', "Done"),])

    seal_no = fields.Char(string="Seal No")
    customer_id = fields.Many2one('res.partner','Returned BY')
    noc_lc_no = fields.Char(string="NOC / LC NO")

    # @api.multi
    # def action_draft(self):

    #     self.state = 'draft'

    # @api.multi
    # def action_done(self):
    #     self.state = 'done'

    def post_action(self):
        self.state = 'done'
        grn = self.env['stock.picking'].search([('origin','=',self.purchase_id.name)],limit=1)
        if grn:
            grn['gate_in_id'] = self.id


    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('Gate_IN') or _('New')
            vals['date_time']= datetime.now()
            vals['state']= 'draft'
        res = super(GateINModule,self).create(vals)
        return res
    
    
    @api.onchange("partner_id")
    def partner_id_domain_pur(self):
        if self.partner_id and self.vendor_type == 'vendor':
            return {"domain": {'partner_id': [('supplier_rank', '>', '0')]}}
        if self.partner_id and self.customer_rank == 'seles_return':
            return {"domain": {'partner_id': [('supplier_rank', '>', '0')]}}

    
    @api.onchange("partner_id","purchase_id")
    def purchase_order_domain_pur(self):
        if self.partner_id : 
            return {"domain": {'purchase_id': [('partner_id', '=', self.partner_id.id)]}}
    
    @api.onchange('purchase_id')
    def _onchange_all_po_line(self):
        order_line=[]
        self['line_id'] = False
        for record in self:
            if record.purchase_id:
                other_model_record = self.env['purchase.order'].search([('id','=', record.purchase_id.id)])
                # raise UserError(other_model_record)
                if other_model_record:
                    for rec in other_model_record:
                        record['partner_id'] = rec.partner_id.id 
                        for line in rec.order_line:
                            order_line.append((0,0,{
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_uom.id,
                                'po_remainig_qty': line.product_qty - line.qty_received,
                                'specs':line.specification
                            }))

                self['line_id'] = order_line

       
class GateInLine(models.Model):
    _name = 'gate.vendor.line'
    _description = "Gate Line"

    gate_module_id = fields.Many2one('gate.in')
    product_id = fields.Many2one('product.product',string='Product')
    product_uom_id = fields.Many2one('uom.uom',string='Unit Of Measurement')
    package = fields.Float(string="Package")
    po_remainig_qty  = fields.Float(string="PO Remaining Qty")
    qty = fields.Float(string='Quantity Received')
    remarks = fields.Char(string="Remarks")

class GateInReturnLine(models.Model):
    _name = 'gate.return.line'
    _description = "Gate IN Return Line"

    gate_module_id = fields.Many2one('gate.in')
    product_id = fields.Many2one('product.product',string='Product')
    product_uom_id = fields.Many2one('uom.uom',string='Unit Of Measurement')
    lot_id = fields.Many2one('stock.lot',string='Batch No / Lot No')
    delivery_challan_number = fields.Char(string="Delivery Challan Number")
    dc_date = fields.Date(string="DC Date")
    qty = fields.Float(string='Quantity')
    remarks = fields.Char(string="Remarks")

    @api.onchange('lot_id')
    def onchange_return_detail(self):
        for rec in self:
            if rec.lot_id:
                stock_move = self.env['stock.move'].search([])
                for move in stock_move:
                    for lot in move.lot_ids:
                        if rec.lot_id.id == lot.id:
                            rec['product_id'] = move.product_id.id
                            rec['delivery_challan_number'] = move.reference
                            rec['product_uom_id'] = move.product_uom.id
                            rec['dc_date'] = move.date.date()



class GateInLine_(models.Model):
    _name = 'gate.other.line'
    _description = "Gate Lines"

    gate_module_id = fields.Many2one('gate.in')
    product = fields.Char(string='Product')
    product_uom = fields.Char(string='Unit Of Measurement')
    qty = fields.Float(string='Quantity  Received')
    remarks = fields.Char(string="Remarks")

class GateOutModule(models.Model):
    _name = "gate.out"
    _description = "Gate Out Module"

    name = fields.Char(string='Gate Reference', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    doc_type = fields.Selection([('g_in', 'Gate In'), ('g_out', 'Gate Out')], string='Document Type')
    customer_type = fields.Selection([('customer', 'Customer'), ('other', 'Other')], string='Gate Out Type')
    gate_type = fields.Selection([('returnable', 'Returnable'), ('nonreturnable', 'Non Returnable')], string='Gate Out Type')
    partner_id = fields.Many2one('res.partner',string='Partner')
    customer_name= fields.Char(string='Customer')
    sale_id = fields.Many2one('stock.picking',string='Delivery Order')
    return_date = fields.Date(string='Return Date',)
    line_id = fields.One2many('gate.customer.line', 'gate_module_id', string="Gate Line")
    line_ids = fields.One2many('gate.other.lines', 'gate_module_id', string="Gate Line")

    location_name = fields.Selection([('fabric', 'FABRIC'),('unit_one', 'Unit One'),('ho', 'HO'),('fg', 'FG'),('e-comm', 'E-Comm'),('whole sale', 'Whole Sale'),('other', 'Other')],string="Location Name")
    sender_name = fields.Char(string="Sender Name")
    department = fields.Char(string="Department")
    department_id = fields.Many2one('stock.location' , string="Department")
    attention_to = fields.Char(string="Attention To")
    date_time = fields.Datetime(string="Date Time")
    receiver_name = fields.Char(string="Receiver Name")
    receiver_number= fields.Char(string="Receiver Number")
    vehicle_number= fields.Char(string="Vehicle Number")
    seal_no= fields.Char(string="Seal No")
    phone  = fields.Binary(string="Photo")
    state = fields.Selection([('draft', "Draft"),('done', "Done"),])

    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('Gate_OUT') or _('New')
            vals['state'] = 'draft'
            vals['date_time']= datetime.now()
        res = super(GateOutModule,self).create(vals)
        return res
    
    def post_action(self):
        raise UserError('tttt')
        self.state = 'done'
    
    @api.onchange("partner_id")
    def partner_id_domain_pur(self):
        if self.partner_id:
            return {"domain": {'partner_id': [('customer_rank', '>', '0')]}}

    
    @api.onchange("partner_id","sale_id")
    def purchase_order_domain_pur(self):
        if self.partner_id:
            return {"domain": {'sale_id': [('partner_id', '=', self.partner_id.id)]}}
    
    
    @api.onchange('sale_id')
    def _onchange_all_so_line(self):
        order_line=[]
        self['line_id'] = False
        for record in self:
            if record.sale_id:
                other_model_record = self.env['stock.picking'].search([('id','=', record.sale_id.id)])
                # raise UserError(other_model_record)
                if other_model_record:
                    for rec in other_model_record:
                        record['partner_id'] = rec.partner_id.id
                        for line in rec.move_ids_without_package:
                            order_line.append((0,0,{
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_uom.id
                            }))
                self['line_id'] = order_line
    
        
class GateOutLine(models.Model):
    _name = 'gate.customer.line'
    _description = "Gate Line"

    gate_module_id = fields.Many2one('gate.out')
    product_id = fields.Many2one('product.product',string='Product')
    product_uom_id = fields.Many2one('uom.uom',string='Unit Of Measurement')
    # product_uom_id = fields.Char(string='Unit Of Measurement')
    no_of_packages = fields.Char(string="No Of Packages")
    qty = fields.Float(string='Quantity')
    remarks = fields.Char(string="Remarks")
        
class GateOutLine_(models.Model):
    _name = 'gate.other.lines'
    _description = "Gate Lines"

    gate_module_id = fields.Many2one('gate.out')
    product = fields.Char(string='Product')
    product_uom = fields.Char(string='Unit Of Measurement')
    no_of_packages = fields.Char(string="No Of Packages")
    qty = fields.Float(string='Quantity')
    remarks = fields.Char(string="Remarks")
