from odoo import models, fields, api
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    grade_id = fields.Many2one('employee.grade', string='Grade')
    grade_title = fields.Char(related='grade_id.designation', string='Grade Title')
    employee_id = fields.Char(string="Employee Id")
    employee_type = fields.Selection([('employee','Employee'),('permanent', 'Permanent'), ('student','Student'),('contractual', 'Contractual'),('trainee','Trainee'),('contractor','Contractor'),('freelance','Freelancer')], string="Employee Type")
    employee_category = fields.Many2one('employee.category', string="Employee Category")
    name_prefix = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.')], string="Name Prefix")



class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    grade_id = fields.Many2one('employee.grade', string='Grade')
    employee_category = fields.Many2one('employee.category', string="Employee Category")
    name_prefix = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.')], string="Name Prefix")
    cnic_exp_date = fields.Date(string='CNIC Expiry Date')
    identification_expiry = fields.Date(string='Identification Expiry Date')
    probation_end_date = fields.Date(string='Probation End Date')
    contract_type = fields.Many2one('hr.contract.type', compute='_compute_contract_type', string='Contract Type', readonly=True)

    @api.depends('employee_id')
    def _compute_contract_type(self):
        for employee in self:
            current_contract = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
            employee.contract_type = current_contract.contract_type_id if current_contract else False


