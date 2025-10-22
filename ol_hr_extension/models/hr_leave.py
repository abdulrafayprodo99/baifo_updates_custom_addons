# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def action_approve(self):
        employee_ids=self.employee_ids.ids
        allocations=self.env['hr.leave.allocation'].search([('holiday_status_id','=',self.holiday_status_id.id)])
        allocations=allocations.filtered(lambda allocation :allocation.employee_id.id in employee_ids)
        if allocations:
            allocation=allocations[0]
            accural_limit=allocation.current_accural_rate
            leaves=self.env['hr.leave'].search([('holiday_status_id','=',self.holiday_status_id.id)])
            leaves = leaves.filtered(lambda leave: 
                leave.employee_ids[0].id == self.employee_ids[0].id and leave.date_from.month == self.date_from.month
                and leave.state =='validate'
            )
            length =sum(leaves.mapped('number_of_days_display'))
            if length + self.number_of_days_display> accural_limit:
                raise UserError("You have availed all your leaves for this month") 
            allocation.leaves_remaining-=self.number_of_days_display
        
        res= super(HrLeave,self).action_approve()   
        return res
    
    def action_refuse(self):
        if self.state=='validate':
            allocations=self.env['hr.leave.allocation'].search([('holiday_status_id','=',self.holiday_status_id.id)])
            allocations=allocations.filtered(lambda allocation :allocation.employee_id.id in self.employee_ids.ids)
            if allocations:
                allocation=allocations[0]
                allocation.leaves_remaining+=self.number_of_days_display
        res= super(HrLeave,self).action_refuse()
        return res

