from odoo import models,fields,api,_
from odoo.exceptions import UserError

class GradeEmployees(models.Model):
    _name = 'employee.grade'

    name = fields.Char('Grades')
    designation = fields.Char('Designation')
    qualification =  fields.Char('Qualification')
    experience = fields.Text('Experience')
    minimum_salary_range = fields.Float('Minimum Salary Range')
    maximum_salary_range = fields.Float('Maximum Salary Range')



