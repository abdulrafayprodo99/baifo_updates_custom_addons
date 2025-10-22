from odoo import models, fields, api, _

class HR_Payslip(models.Model):
    _inherit = 'hr.payslip.run'

    def action_validate(self): 
        res=super(HR_Payslip,self).action_validate()
        for run in self:
            for slip in run.slip_ids:
                if slip.move_id: 
                    try:
                        slip.move_id.action_post()
                    except Exception as e:
                        continue
        return res

