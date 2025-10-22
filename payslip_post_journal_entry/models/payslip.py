from odoo import models, api, _
from odoo.exceptions import UserError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    # def action_post_journal_entry(self):
    #     for rec in self:
    #         for payslip in rec.slip_ids:
    #             payslip.move_id.action_post()