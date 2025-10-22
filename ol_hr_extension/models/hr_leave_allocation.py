# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    
    months_remaining=fields.Integer("Months Remaining")
    current_accural_rate=fields.Float("Accural Rate")
    leaves_remaining=fields.Integer("Leaves Remaining")

    def _compute_accural_rate(self):
        for rec in self:
            rec.current_accural_rate=0.0
            if rec.months_remaining and rec.leaves_remaining:
                rec.current_accural_rate=rec.leaves_remaining//rec.months_remaining 


    def action_confirm(self):
        self.ensure_one()
        res= super(HrLeaveAllocation,self).action_confirm()
        self.leaves_remaining=self.number_of_days_display
        return res

    def get_months_remaining(self):
        if self.date_to:
            today = date.today()
            end_date=self.date_to
            days=end_date-today
            months=days.days// 30
            return months
    
    def fields_population(self):
        for rec in self:
            rec._compute_accural_rate()
            rec.months_remaining=rec.get_months_remaining()




