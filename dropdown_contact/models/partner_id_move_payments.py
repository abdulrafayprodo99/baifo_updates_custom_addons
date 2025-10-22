from odoo import models, fields,api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'



    customer_domain = fields.Many2many('res.partner', compute="_compute_customer_domain", string="Customers")
    vendor_domain = fields.Many2many('res.partner', compute="_compute_vendor_domain", string="Vendors")

    @api.depends("journal_id")
    def _compute_customer_domain(self):
        for rec in self:
            # raise UserError(str(rec.move_type))
            # Search for all customers
            customer_ids = rec.env['res.partner'].search([('supplier_rank', '=', 0)])  # Filter to include only customers
            rec.customer_domain = customer_ids.ids  # Set the Many2many field to the found customers

    @api.depends("journal_id")
    def _compute_vendor_domain(self):
        for rec in self:
            # raise UserError(str(rec.move_type))
            # Search for all vendors
            vendor_ids = rec.env['res.partner'].search([('customer_rank', '=', 0)])  # Filter to include only vendors
            rec.vendor_domain = vendor_ids.ids  # Set the Many2many field to the found vendors

    new_partner_id = fields.Many2one('res.partner' , string="New Partner Id" )


    partner_ids = fields.Many2many('res.partner', compute="_compute_domain", string="Domain")


    # @api.depends("journal_id")
    # def _compute_customer_domain(self):
    #     for rec in self:
    #         # Search for all customers
    #         customer_ids = rec.env['res.partner'].search([('supplier_rank', '=', 0)]) 
    #         raise UserError(str(customer_ids.read())) # Filter to include only customers
    #         rec.customer_domain = customer_ids.ids  # Set the Many2many field to the found customers

    # @api.depends("journal_id")
    # def _compute_vendor_domain(self):
    #     for rec in self:
    #         # Search for all vendors
    #         vendor_ids = rec.env['res.partner'].search([('customer_rank', '=', 0)])  # Filter to include only vendors
    #         rec.vendor_domain = vendor_ids.ids  # Set the Many2many field to the found vendors





    @api.depends("move_type")
    def _compute_domain(self):
        for rec in self:
            rec.partner_ids = None
            # raise UserError(str(rec.move_type))
            if rec.move_type == 'out_refund' or  rec.move_type == 'out_invoice':
                customer_ids = rec.env['res.partner'].search([('customer_rank', '>', 0 )])
                rec.partner_ids = customer_ids 
            elif rec.move_type == 'in_refund' or  rec.move_type == 'in_invoice':
            # Search for all vendors (those with supplier_rank > 0 and customer_rank == 0)
                vendor_ids = rec.env['res.partner'].search([('supplier_rank', '>', '0')])
                rec.partner_ids = vendor_ids 


    @api.onchange('new_partner_id')
    def _onchange_new_partner_id(self):
        if self.new_partner_id:
            self.partner_id = self.new_partner_id
    




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    vendor_domain = fields.One2many('res.partner', compute="_compute_vendor_domain", string="Vendors")   
    customer_domain = fields.One2many('res.partner', compute="_compute_customer_domain", string="Customers")

    new_partner_id = fields.Many2one('res.partner' , string="New Partner Id" )


    partner_ids = fields.Many2many('res.partner', compute="_compute_domain", string="Domain")


    # @api.depends("journal_id")
    # def _compute_customer_domain(self):
    #     for rec in self:
    #         # Search for all customers
    #         customer_ids = rec.env['res.partner'].search([('supplier_rank', '=', 0)]) 
    #         raise UserError(str(customer_ids.read())) # Filter to include only customers
    #         rec.customer_domain = customer_ids.ids  # Set the Many2many field to the found customers

    # @api.depends("journal_id")
    # def _compute_vendor_domain(self):
    #     for rec in self:
    #         # Search for all vendors
    #         vendor_ids = rec.env['res.partner'].search([('customer_rank', '=', 0)])  # Filter to include only vendors
    #         rec.vendor_domain = vendor_ids.ids  # Set the Many2many field to the found vendors


    @api.depends("journal_id")
    def _compute_customer_domain(self):
        for rec in self:
            # Search for all customers (those with customer_rank > 0 and supplier_rank == 0)
            customer_ids = rec.env['res.partner'].search([]).filtered(lambda x: x.customer_rank > 0 and x.supplier_rank < 1)
            rec.customer_domain = customer_ids#[(4,i.id) for i in customer_ids]
            # raise UserError(str(rec.customer_domain.mapped('name')))
              # Set the Many2many field to the found customers
            # Optionally, raise a UserError to debug and check the customer results
            # raise UserError(str(customer_ids.read(['name', 'customer_rank', 'supplier_rank'])))
    
    @api.depends("journal_id")
    def _compute_vendor_domain(self):
        for rec in self:
            # Search for all vendors (those with supplier_rank > 0 and customer_rank == 0)
            vendor_ids = rec.env['res.partner'].search([('supplier_rank', '>', 0), ('customer_rank', '=', 0)])
            rec.vendor_domain = vendor_ids  # Set the Many2many field to the found vendors
            # Optionally, raise a UserError to debug and check the vendor results
            # raise UserError(str(vendor_ids.read(['name', 'customer_rank', 'supplier_rank'])))



    @api.depends("payment_type")
    def _compute_domain(self):
        for rec in self:
            rec.partner_ids = None
            if rec.payment_type == 'inbound':
                customer_ids = rec.env['res.partner'].search([('customer_rank', '>', 0 )])
                rec.partner_ids = customer_ids 
            elif rec.payment_type == 'outbound':
            # Search for all vendors (those with supplier_rank > 0 and customer_rank == 0)
                vendor_ids = rec.env['res.partner'].search([('supplier_rank', '>', '0')])
                rec.partner_ids = vendor_ids 


    @api.onchange('new_partner_id')
    def _onchange_new_partner_id(self):
        if self.new_partner_id:
            self.partner_id = self.new_partner_id
    



# from odoo import models, fields

# class StockPickingInherit(models.Model):
#     _inherit = 'stock.picking'

#     partner_id = fields.Many2one(
#         'res.partner', 'Contact',
#         domain="[('type', '=', 'delivery'), ('parent_id', '=', x_studio_vendor)]",
#         check_company=True,
#         required=True,
#         default=False,
#         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
#     )
