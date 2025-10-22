from odoo import models, fields

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_code = fields.Char(
        string='Employee Code',
        related='employee_id.employee_id',
        store=True,
        readonly=True
    )
        