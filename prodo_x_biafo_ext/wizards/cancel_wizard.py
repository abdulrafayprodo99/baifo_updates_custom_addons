from odoo import fields, models
from odoo.exceptions import UserError

class RejectionNote(models.TransientModel):
    _name = 'cancel.wizard'
    _description = 'Cancel Wizard'

    rejection_note = fields.Char(string='Cancel Note')
    
    def action_cancel(self):
        if self['rejection_note']:
            # RIQ -
            if self._context.get('active_model') == "purchase.request":
                pr = self.env['purchase.request'].browse(
                    self._context.get('active_ids', [])
                )
                if pr:
                    if pr['cancel_note']:
                        pr['cancel_note'] += ' ● ' + str(self.rejection_note) + '\n' 
                    else:
                        pr['cancel_note'] = ' ● ' + str(self.rejection_note) + '\n' 
                    self.pr_cancel(pr)
                    return pr

            # Gate Out
            if self._context.get('active_model') == "gate.out":
                out = self.env['gate.out'].browse(
                    self._context.get('active_ids', [])
                )
                if out:
                    if out['cancel_note']:
                        out['cancel_note'] += ' ● ' + str(self.rejection_note) + '\n' 
                    else:
                        out['cancel_note'] = ' ● ' + str(self.rejection_note) + '\n' 
                    self.out_cancel(out)
                    return out

            # Stock Picking
            if self._context.get('active_model') == "stock.picking":
                picking = self.env['stock.picking'].browse(
                    self._context.get('active_ids', [])
                )
                if picking:
                    if picking['cancel_note']:
                        picking['cancel_note'] += ' ● ' + str(self.rejection_note) + '\n' 
                    else:
                        picking['cancel_note'] = ' ● ' + str(self.rejection_note) + '\n' 
                    self.picking_cancel(picking)
                    return picking
            #purchase order
            if self._context.get('active_model') == "purchase.order":
                picking = self.env['purchase.order'].browse(
                    self._context.get('active_ids', [])
                )
                if picking:
                    if picking['cancel_note']:
                        picking['cancel_note'] += ' ● ' + str(self.rejection_note) + '\n'
                    else:
                        picking['cancel_note'] = ' ● ' + str(self.rejection_note) + '\n'
                    self.with_context(cancel=True).button_cancel(picking)
                    return picking

    def pr_cancel(self, pr):
        pr.action_cancel()
    
    def picking_cancel(self, picking):
        picking.action_cancel()
    
    def out_cancel(self, out):
        out.state = "cancel"
