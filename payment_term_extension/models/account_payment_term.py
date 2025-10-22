from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    order_type = fields.Selection(
        selection=[('customer', 'Customer'), ('vendor', 'Vendor')],
        string='Order Type',
        required=True
    )





class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'draft' : [('readonly', False)],
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    payment_term_id = fields.Many2one(
        'account.payment.term',
        'Payment Terms',
        states=READONLY_STATES,
        required=True,
        domain="[('order_type', '=', 'vendor'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        compute='_compute_payment_term_id',
        store=True,
        required=True,
        precompute=True,
        check_company=True,
        domain="[('order_type', '=', 'customer'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )







class ResPartner(models.Model):
    _inherit = 'res.partner'


    property_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Customer Payment Terms',
        company_dependent=True,
        domain="[('order_type', '=', 'customer'), ('company_id', 'in', [current_company_id, False])]",
        help="This payment term will be used instead of the default one for sales orders and customer invoices"
    )

    property_supplier_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Vendor Payment Terms',
        company_dependent=True,
        domain="[('order_type', '=', 'vendor'), ('company_id', 'in', [current_company_id, False])]",
        help="This payment term will be used instead of the default one for purchase orders and vendor bills"
    )

    is_payment_term_set = fields.Boolean(
        string="Is Any Payment Term Set",
        compute="_compute_is_payment_term_set",
        store=True
    )

    @api.depends('property_payment_term_id', 'property_supplier_payment_term_id')
    def _compute_is_payment_term_set(self):
        for rec in self:
            rec.is_payment_term_set = bool(rec.property_payment_term_id or rec.property_supplier_payment_term_id)

