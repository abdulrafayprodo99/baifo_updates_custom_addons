from odoo import models, fields

class StockPickingApproval(models.Model):
    _inherit = 'stock.picking'

    approval_state_return_picking = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('verified', 'Verified'),
        ('approved', 'Approved')
    ], string="Approval State", default='draft', tracking=True)

    def action_prepared(self):
        self.write({'approval_state_return_picking': 'prepared'})

    def action_verified(self):
        self.write({'approval_state_return_picking': 'verified'})

    def action_approved(self):
        self.write({'approval_state_return_picking': 'approved'})
