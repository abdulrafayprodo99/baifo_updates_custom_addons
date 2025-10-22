# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.constrains('move_id')
    def populate_analytic_distribution(self):
        for rec in self:
            if rec.move_id and rec.employee_id.analytic_distribution:
                if rec.move_id.line_ids:
                    for line in rec.move_id.line_ids:
                        current_distribution = line.analytic_distribution or {}
                        for i in current_distribution:
                            current_distribution[i]=50.00
                        current_distribution[rec.employee_id.analytic_distribution.id] = 50.0 
                        line.analytic_distribution = current_distribution

        return True
    

 