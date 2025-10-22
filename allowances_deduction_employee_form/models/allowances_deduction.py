from odoo import models,fields,api,_
from odoo.exceptions import UserError

class AllowancesDeduction(models.Model):
    _name="allowances.deduction"
    _rec_name = 'emp_id'

    emp_id = fields.Char(string='Employee ID')
    employee_id = fields.Many2one(string="Employee Name",comodel_name = 'hr.employee')
    job_id = fields.Many2one('hr.job', string='Designation')
    pf_employee_contribution = fields.Float(string="PF Employee Contribution")
    pf_employer_contribution = fields.Float(string="PF Employer Contribution")
    food_employee_contribution = fields.Float(string="Food Employee Contribution")
    food_employer_contribution = fields.Float(string="Food Employer Contribution")
    ss_employer_contribution = fields.Float(string='Social Security Employer Contribution', readonly=True)
    eobi_contribution = fields.Float(string="EOBI Contribution", readonly=True)
    eobi_employer_contribution = fields.Float(string="EOBI Employer Contribution", readonly=True)
    professional_tax = fields.Float(string="Professional Tax")
    manual_eobi = fields.Float(string="Manual EOBI")
    year = fields.Selection(
        selection=[(str(year), str(year)) for year in range(2000, 2031)],  # Adjust the range as needed
        string='Year',
    )
    month = fields.Selection(
        selection=[
            ('january', 'January'),
            ('february', 'February'),
            ('march', 'March'),
            ('april', 'April'),
            ('may', 'May'),
            ('june', 'June'),
            ('july', 'July'),
            ('august', 'August'),
            ('september', 'September'),
            ('october', 'October'),
            ('november', 'November'),
            ('december', 'December'),
        ],
        string='Month',
        
    )
    arrears = fields.Float(string='Arrears')
    other_allowance = fields.Float(string='Other Allowance')
    advance_from_employer = fields.Float(string='Advance From Employer')
    other_deduction = fields.Float(string='Other Deduction')
    zakat = fields.Float(string='Zakat')
    donation = fields.Float(string='Donation')
    wht_on_property = fields.Float(string='WHT on Property')
    wht_on_vehicle = fields.Float(string='WHT on Vehicle')
    wht_on_telephone = fields.Float(string='WHT on Telephone')
    other_tax = fields.Float(string='Other Tax')
    provident_fund_loan = fields.Float(string="Provident Fund Loan" )
    overtime = fields.Integer(string='Overtime')
    excessive_leaves = fields.Integer(string='Excessive Leaves')
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
             if rec.employee_id:
                 rec.job_id = rec.employee_id.job_id.id
                 rec.emp_id = rec.employee_id.employee_id