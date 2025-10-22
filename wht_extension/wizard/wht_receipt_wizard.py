from odoo import models, fields, api

class WHTReceiptWizard(models.TransientModel):
    _name = 'wht.receipt.wizard'
    _description = 'WHT Receipt Wizard'

    tax_date = fields.Date(string='Tax Date')
    challan_no = fields.Char(string='Challan No')
    due_date = fields.Date(string='Due Date')
    bank_name = fields.Char(string='Bank')
    branch = fields.Char(string='Branch')
    cheque_to_be_issued = fields.Char(string='Cheque # Issued')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if len(active_ids) == 1:
            line = self.env['payment.wht.line'].browse(active_ids[0])
            res['tax_date'] = line.tax_date
            res['due_date'] = line.due_date
        return res

    def apply_values(self):
        active_ids = self.env.context.get('active_ids')
        lines = self.env['payment.wht.line'].browse(active_ids)
        for line in lines:
            line.write({
                'tax_date': self.tax_date,
                'challan_no': self.challan_no,
                'bank_name': self.bank_name,
                'branch': self.branch,
                'cheque_to_be_issued': self.cheque_to_be_issued,
                'due_date': self.due_date,  # optional: only update if needed
            })
