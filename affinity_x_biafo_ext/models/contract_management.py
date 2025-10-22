from odoo import api, fields, models,_
from odoo.exceptions import UserError

class ContractManagement(models.Model):
    _name = "contract.management"
    _description = "Contract Management "

    name = fields.Char(string='Name',readonly=True)
    contrect_id = fields.Char(string='Contract Id',readonly=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", domain=[('contract_id','=',False)])
    sale_id = fields.Many2one('sale.order', string="Sale Order", domain=[('contract_id','=',False)])
    partner_id = fields.Many2one('res.partner', string="Partner", compute='compute_partner_id')
    doc_type = fields.Selection(selection=[('sale','Sale'),('purhcase','Purchase')], string="Document")
    contrect_no = fields.Char("Contrect No" , required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    attachment = fields.Binary('Attachment')
    attachment_filename = fields.Char('Attachment Filename')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val['doc_type'] == 'sale':
                val['name'] = self.env['ir.sequence'].next_by_code('cms')
                val['contrect_id'] = val['name']
            if val['doc_type'] == 'purhcase':
                val['name'] = self.env['ir.sequence'].next_by_code('cmo')
                val['contrect_id'] = val['name']
        return super().create(vals)
    
    @api.depends('sale_id','purchase_id')
    def compute_partner_id(self):
        for rec in self:
            rec['partner_id'] = False
            if rec['doc_type'] == 'sale':
                rec['partner_id'] = rec.sale_id.partner_id.id 
            if rec['doc_type'] == 'purhcase':
                rec['partner_id'] = rec.purchase_id.partner_id.id


    def update_contract_id_on_sale_or_purchase(self):
        for rec in self:
            if rec.sale_id or rec.purchase_id:
                rec['sale_id']['contract_id'] = rec.id
                rec['purchase_id']['contract_id'] = rec.id
            else:
                raise UserError('Please Select Sale Order OR Purchase Order')
            
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise UserError("End Date cannot be less than Start Date!")