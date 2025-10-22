from odoo import models, fields, api

class CPRMUpdateWizard(models.TransientModel):
    _name = 'cprm.update.wizard'
    _description = 'Update CPRM No'

    cprm_no = fields.Char(string='CPRM No')

    def apply_cprm_update(self):
        active_ids = self.env.context.get('active_ids', [])
        lines = self.env['payment.wht.line'].browse(active_ids)
        for line in lines:
            line.write({
                'cprm_no': self.cprm_no,
            })
