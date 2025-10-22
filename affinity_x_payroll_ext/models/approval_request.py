# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import _, api, fields, models

class TravelAuth(models.Model):
    _inherit = "approval.request"


    employee_id = fields.Many2one("hr.employee", string="Employee")
    job_position = fields.Many2one(related="employee_id.job_id", string="Job Position")
    travel_purpose = fields.Char(sting="Travel Purpose")
    travel_type = fields.Selection(selection=[('local','Local'),('intr','International Travel')])
    travel_from = fields.Selection(selection=[('islamabad','Islamabad'),('other','Other')], string="Travel From")
    other_from = fields.Char(string="Other Travel From")
    travel_to = fields.Char(string='Travel To')
    departure_date = fields.Date(string="Departure Date")
    return_date = fields.Date(string="Return Date")

    air_ticket = fields.Boolean(string="Air Ticket")
    transport = fields.Boolean(string="Transport")
    accommodation = fields.Boolean(string="Accommodation")
    cash_advance = fields.Char(string="Cash Advance")
    currency_id =fields.Many2one('res.currency',string="Currency")
    purpose = fields.Char(string="Purpose")

    approve_by = fields.Many2one('res.users',string="Approve By")
    approve_time = fields.Datetime(string="Date")

    # Hr Department

    type_allowance = fields.Selection(selection=[('field','Field'),('ta_da','TA/DA')],string="Type Of Allowance")
    no_days = fields.Char(string="No of Days")
    Amount = fields.Float(string="Amount")
    Authorized_hr_setting = fields.Many2one('res.users',string="Authorized HR Setting")
    authorized_time = fields.Datetime(string='Date')

    travel_desk_id = fields.One2many('travel.desk','travel_auth_id', string="Travel Desk")
    finance_depart_id = fields.One2many('finance.depart','travel_auth_id', string="Finance Depart")

class TravelDesk(models.Model):
    _name="travel.desk"
    
    travel_auth_id = fields.Many2one('approval.request',string="Travel Auth")
    name = fields.Char(string="Description")
    amount = fields.Float(string="Estimated Amount")


class FinanceDepartment(models.Model):
    _name="finance.depart"
    
    travel_auth_id = fields.Many2one('approval.request',string="Travel Auth")
    name = fields.Char(string="Description")
    amount = fields.Float(string="Amount")


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    _description = 'Approval Category'

    approval_type = fields.Selection(selection_add=[('travel', 'Travel')])