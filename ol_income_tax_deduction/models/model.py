from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime
from odoo.exceptions import UserError
import logging
from odoo.addons.hr_payroll.models.hr_payslip import HrPayslip as BaseHrPayslip


# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import random

from collections import defaultdict, Counter
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import AND
from odoo.tools import float_round, date_utils, convert_file, html2plaintext, is_html_empty, format_amount
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)

class HR_Contract(models.Model):
    _inherit = 'hr.contract'

    start_probation = fields.Date(string='Start of Probation')
    end_probation = fields.Date(string='End of Probation')
    increment = fields.Float(string='Increment', compute='_compute_increment')
    taxable_income = fields.Float(string='Taxable Income')
    computed_taxable_income = fields.Float(string='Gross Income Tax', compute='_compute_taxable_income')
    tax_months = fields.Integer(string='Tax Paid Months')
    previous_tax_paid = fields.Float(string='Previous Tax Paid')#, compute='_compute_previous_tax_paid')
    fiscal_year = fields.Selection(
        selection=[(str(year), str(year)) for year in range(2000, 2031)],  # Adjust the range as needed
        string='Year',
    )
    minimum_wage = fields.Float(string='Minimum Wage Social Security')
    minimum_wage_eobi = fields.Float(string='Minimum Wage EOBI')
    tax_liability = fields.Float(string='Tax Liability', compute='_compute_tax_liability')
    monthly_tax_deduction = fields.Float(string='Monthly Tax Deduction', compute='_compute_monthly_tax_liability')
    final_tax_liability = fields.Float(string='Final Tax Liability', compute='_compute_final_tax_liability')
    zakat = fields.Float(string='Zakat', compute='_compute_zakat')
    total_deduction_tax = fields.Float(string='Total Deduction Tax', compute='_compute_total_deduction_tax')
    manual_eobi = fields.Float(string="Manual EOBI", compute='_compute_allowance_deductions')
    pf_employee_contribution = fields.Float(string="PF Employee Contribution", compute='_compute_allowance_deductions')
    pf_employer_contribution = fields.Float(string="PF Employer Contribution", compute='_compute_allowance_deductions')
    food_employee_contribution = fields.Float(string="Food Charges", compute='_compute_allowance_deductions')
    food_employer_contribution = fields.Float(string="Food Employer Contribution", compute='_compute_allowance_deductions')
    other_allowance = fields.Float(string='Other Allowance', compute='_compute_allowance_deductions')
    other_deduction = fields.Float(string='Other Deduction', compute='_compute_allowance_deductions')
    professional_tax = fields.Float(string='Professional Tax', compute='_compute_allowance_deductions')
    advance_from_employer = fields.Float(string='Advance From Employer', compute='_compute_allowance_deductions')
    provident_fund_loan = fields.Float(string="Provident Fund Loan", compute='_compute_allowance_deductions')
    income_tax_payable = fields.Float(string='Income Tax Payable', compute='_compute_income_tax_payable')
    overtime = fields.Float(string='Overtime', compute='_compute_allowance_deductions')
    excessive_leaves = fields.Float(string='Excessive Leaves', compute='_compute_allowance_deductions')
    arrears = fields.Float(string='Arrears', compute='_compute_allowance_deductions')

    def calculate_pf(self):
        for contract in self:
            basic = contract.wage / 1.5
            arrears = contract.arrears / 1.5
            result = (basic + arrears) * 0.1
            return result

    @api.depends('tax_liability', 'total_deduction_tax')
    def _compute_income_tax_payable(self):
        for contract in self:
            contract.income_tax_payable = abs(contract.tax_liability - contract.total_deduction_tax)
            
    def _compute_tax_liability(self):
        for contract in self:
            annual_salary, taxable_months = contract.Income_Tax_Deduction()
            months_tax_paid = contract.tax_months
            paid_tax = contract.previous_tax_paid
            current_tax = 0.0
            computed_income = contract.computed_taxable_income
            

            if computed_income > 600000 and computed_income <= 1200000:
                # raise UserError(str(computed_income))
                tax = ((computed_income - 600000) * 1) / 100
                if tax > 0:
                    # raise UserError(str(taxable_months))
                    monthly_tax = tax / (taxable_months + months_tax_paid)
                    current_tax = monthly_tax * (taxable_months + months_tax_paid)
                    # current_tax -= paid_tax
                    # current_tax -= contract.total_deduction_tax

            elif computed_income > 1200000 and computed_income <= 2200000:
                tax = ((computed_income - 1200000) * 11) / 100
                tax += 6000
                if tax > 0:
                    monthly_tax = tax / (taxable_months + months_tax_paid)
                    current_tax = monthly_tax * (taxable_months + months_tax_paid)
                    # current_tax -= paid_tax
                    # current_tax -= contract.total_deduction_tax

            elif computed_income > 2200000 and computed_income <= 3200000:
                tax = ((computed_income - 2200000) * 23) / 100
                tax += 116000
                if tax > 0:
                    monthly_tax = tax / (taxable_months + months_tax_paid)
                    current_tax = monthly_tax * (taxable_months + months_tax_paid)
                    # current_tax -= paid_tax
                    # current_tax -= contract.total_deduction_tax

            elif computed_income > 3200000 and computed_income <= 4100000:
                tax = ((computed_income - 3200000) * 30) / 100
                tax += 346000
                if tax > 0:
                    monthly_tax = tax / (taxable_months + months_tax_paid)
                    current_tax = monthly_tax * (taxable_months + months_tax_paid)
                    # current_tax -= paid_tax
                    # current_tax -= contract.total_deduction_tax

            elif computed_income > 4100000:
                tax = ((computed_income - 4100000) * 35) / 100
                tax += 616000
                current_tax = tax  # - paid_tax  - contract.total_deduction_tax

            contract.tax_liability = max(abs(current_tax), 0.0)

            if computed_income > 10000000:
                extra = contract.tax_liability * 0.09
                contract.tax_liability += extra

    @api.depends('zakat')
    def _compute_taxable_income(self):
        for contract in self:
            # Fetch zakat from allowances.deduction for the current employee and year
            allowance_deduction = self.env['allowances.deduction'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('year', '=', datetime.today().year)
            ], limit=1)
            zakat = allowance_deduction.zakat if allowance_deduction else 0.0
            # Calculate taxable income
            contract.computed_taxable_income = contract.taxable_income - zakat   
        

    def Income_Tax_Deduction(self):
        current_contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
        current_date = datetime.today().date()
        fiscal_year = False 
        taxable_months = 0
        annual_salary = 0
        if current_date.month in [7,8,9,10,11,12]:
            fiscal_year = current_date.year
        else:
            fiscal_year = current_date.year - 1
        last_day_of_fiscal_year =  datetime(fiscal_year+1, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day)).date()
        first_day_of_fiscal_year = (datetime(fiscal_year, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day))+timedelta(days=1)).date()
        # If running cotract has an end date
        if current_contract.date_end:
            # If running contract was started with or before fiscal year and ends with or after fiscal year
            if current_contract.date_start <= first_day_of_fiscal_year and current_contract.date_end >= last_day_of_fiscal_year:
                annual_salary = current_contract.wage * 12
                taxable_months = 12
            # Else we find all the contracts for employee and search through them
            else:
                relevant_contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','in',['open','close'])])
                total_amount = 0
                for contract in relevant_contracts:
                    # If contract was started with or after fiscal year and ends with or before fiscal year
                    if contract.date_start >= first_day_of_fiscal_year and contract.date_end <= last_day_of_fiscal_year:
                        difference = relativedelta(contract.date_end, contract.date_start)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                    # If contract was started with or before fiscal year and ends with or before fiscal year
                    elif contract.date_start <= first_day_of_fiscal_year and (contract.date_end <= last_day_of_fiscal_year and contract.date_end > first_day_of_fiscal_year):
                        difference = relativedelta(contract.date_end, first_day_of_fiscal_year)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                    # If contract was started with or after fiscal year and ends with or after fiscal year
                    elif contract.date_start >= first_day_of_fiscal_year and contract.date_end >= last_day_of_fiscal_year:
                        difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                annual_salary = total_amount
        # If running contract does not have an end date
        else:
            # If running contract was started with or before fiscal year
            if current_contract.date_start <= first_day_of_fiscal_year:
                annual_salary = current_contract.wage * 12
                taxable_months = 12
            # If running contract was started after fiscal year
            else:
                relevant_contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','in',['open','close'])])
                total_amount = 0
                for contract in relevant_contracts:
                    if contract.date_end:
                        # If contract was started with or after fiscal year and ends with or before fiscal year
                        if contract.date_start >= first_day_of_fiscal_year and contract.date_end <= last_day_of_fiscal_year:
                            difference = relativedelta(contract.date_end, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                        # If contract was started with or before fiscal year and ends with or before fiscal year
                        elif contract.date_start <= first_day_of_fiscal_year and (contract.date_end <= last_day_of_fiscal_year and contract.date_end > first_day_of_fiscal_year):
                            difference = relativedelta(contract.date_end, first_day_of_fiscal_year)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                        # If contract was started with or after fiscal year and ends with or after fiscal year
                        elif contract.date_start >= first_day_of_fiscal_year and contract.date_end >= last_day_of_fiscal_year:
                            difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                    else:
                        if contract.date_start >= first_day_of_fiscal_year:
                            difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                annual_salary = total_amount
        return annual_salary, taxable_months
        
    @api.depends('wage')
    def _compute_increment(self):
        for contract in self:
            current_contract = self.env['hr.contract'].search([('employee_id', '=', contract.employee_id.id), ('state', '=', 'open')], limit=1)
            canceled_contracts = self.env['hr.contract'].search([('employee_id', '=', contract.employee_id.id), ('state', '=', 'cancel')])
            if current_contract and canceled_contracts:
                # Assuming the last canceled contract is the one to compare with
                last_canceled_contract = canceled_contracts[-1]
                contract.increment = current_contract.wage - last_canceled_contract.wage
            else:
                contract.increment = 0.0  # No increment if no canceled contracts

    # @api.depends('taxable_income', 'tax_months')
    # def _compute_previous_tax_paid(self):
    #     for record in self:
    #         # Assuming previous tax paid is calculated as annual taxable income divided by 12 times the number of tax months
    #         record.previous_tax_paid = (record.taxable_income / 12) * record.tax_months if record.tax_months else 0.0


    # @api.depends('income_tax_payable', 'previous_tax_paid')
    # def _compute_monthly_tax_liability(self):
    #     for contract in self:
    #         if contract.final_tax_liability > 0:
    #             contract.monthly_tax_deduction = contract.final_tax_liability / (12 - contract.tax_months) if contract.tax_months < 12 else 0.0
    #         else:
    #             contract.monthly_tax_deduction = 0.0
    @api.depends('income_tax_payable', 'previous_tax_paid')
    def _compute_monthly_tax_liability(self):
        for contract in self:
            try:
                # Ensure that tax_months is less than 12 to avoid division by zero
                if contract.final_tax_liability > 0:
                    if contract.tax_months < 12:
                        contract.monthly_tax_deduction = contract.final_tax_liability / (12 - contract.tax_months)
                    else:
                        contract.monthly_tax_deduction = 0.0
                else:
                    contract.monthly_tax_deduction = 0.0

                # Ensure `monthly_tax_deduction` is a valid number before formatting
                if isinstance(contract.monthly_tax_deduction, (int, float)):
                    contract.monthly_tax_deduction = "{:.2f}".format(round(contract.monthly_tax_deduction, 2))
                else:
                    contract.monthly_tax_deduction = 0.00
            except Exception as e:
                # Catch any exception and log it (optional)
                _logger.exception(f"Error computing monthly tax liability for contract {contract.id}: {e}")
                contract.monthly_tax_deduction = "0.00"



    @api.depends('income_tax_payable', 'previous_tax_paid')
    def _compute_final_tax_liability(self):
        for contract in self:
            contract.final_tax_liability = contract.income_tax_payable - contract.previous_tax_paid
    

    @api.depends('employee_id')
    def _compute_zakat(self):
        for contract in self:
            # Fetch zakat from allowances.deduction for the current employee and year
            allowance_deduction = self.env['allowances.deduction'].search([
                ('employee_id', '=', contract.employee_id.id),
                # ('year', '=', datetime.today().year),
                # ('month', '=', datetime.today().strftime('%B').lower()) 
            ], order="id desc",limit=1)
            contract.zakat = allowance_deduction.zakat if allowance_deduction else 0.0


        # for contract in self:
        #     # Get the current year
        #     current_year = datetime.today().year
        #     # Define the fiscal year range
        #     start_date = datetime(current_year, 7, 1)  # July 1st of the current year
        #     end_date = datetime(current_year + 1, 6, 30)  # June 30th of the next year
            
        #     # Search for all payslips for the employee within the fiscal year range
        #     payslips = self.env['hr.payslip'].search([
        #         ('employee_id', '=', contract.employee_id.id),
        #         ('date_from', '>=', start_date),
        #         ('date_to', '<=', end_date),
        #         ('date_from', '>=', contract.date_start)
        #     ])
            
        #     total_zakat = 0.0  # Initialize total zakat
            
        #     # Iterate through each payslip to get the year and calculate zakat
        #     for payslip in payslips:
        #         allowance_deductions = self.env['allowances.deduction'].search([
        #             ('employee_id', '=', contract.employee_id.id),
        #             ('year', '=', payslip.date_from.year)  # Use the year from the payslip
        #         ])
        #         # Sum the zakat from all found allowance deductions for the specific year
        #         total_zakat += sum(allowance.zakat for allowance in allowance_deductions)
            
        #     contract.zakat = total_zakat  # Assign the total zakat to the contract

    @api.depends('employee_id')
    def _compute_total_deduction_tax(self):
        for contract in self:
            # Fetch allowances.deduction for the current employee and year
            allowance_deduction = self.env['allowances.deduction'].search([
            ('employee_id', '=', contract.employee_id.id),
            ('year', '=', datetime.today().year)
            ], limit=1)
            if allowance_deduction:
                contract.total_deduction_tax = (
                    allowance_deduction.donation +
                    allowance_deduction.wht_on_property +
                    allowance_deduction.wht_on_vehicle +
                    allowance_deduction.wht_on_telephone +
                    allowance_deduction.other_tax
                )
            else:
                contract.total_deduction_tax = 0.0 
        # for contract in self:
        #     # Get the current year and define the fiscal year range
        #     current_year = datetime.today().year
        #     start_date = datetime(current_year, 7, 1)  # July 1st of the current year
        #     end_date = datetime(current_year + 1, 6, 30)  # June 30th of the next year
            
        #     # Get all payslips for the employee within the fiscal year range
        #     payslips = self.env['hr.payslip'].search([
        #         ('employee_id', '=', contract.employee_id.id),
        #         ('date_from', '>=', start_date),
        #         ('date_to', '<=', end_date),
        #         ('date_from', '>=', contract.date_start)
        #     ])
            
        #     # Create a dictionary to hold total deductions for each employee
        #     employee_deductions = defaultdict(float)

        #     # Iterate through each payslip to get the year and sum deductions
        #     for payslip in payslips:
        #         allowances = self.env['allowances.deduction'].search([
        #             ('employee_id', '=', contract.employee_id.id),
        #             ('year', '=', payslip.date_from.year)  # Use the year from each payslip
        #         ])
                
        #         # Sum the specified deductions for each employee
        #         for allowance in allowances:
        #             employee_deductions[allowance.employee_id.id] += (allowance.donation + 
        #                                                             allowance.wht_on_property + 
        #                                                             allowance.wht_on_vehicle + 
        #                                                             allowance.wht_on_telephone + 
        #                                                             allowance.other_tax)
            
        #     # Assign the computed total deduction tax to the current contract
        #     contract.total_deduction_tax = employee_deductions.get(contract.employee_id.id, 0.0)

    @api.depends('employee_id')
    def _compute_allowance_deductions(self):
        for contract in self:
            allowance_deduction = self.env['allowances.deduction'].search([
                ('employee_id', '=', contract.employee_id.id),
                # ('year', '=', datetime.today().year),
                # ('month', '=', datetime.today().strftime('%B').lower()) 
            ], order="id desc",limit=1)
            # raise UserError(str(allowance_deduction.employee_id.name))
            if allowance_deduction:
                contract.pf_employee_contribution = allowance_deduction.pf_employee_contribution
                contract.pf_employer_contribution = allowance_deduction.pf_employer_contribution
                contract.food_employee_contribution = allowance_deduction.food_employee_contribution
                contract.food_employer_contribution = allowance_deduction.food_employer_contribution
                contract.other_allowance = allowance_deduction.other_allowance
                contract.other_deduction = allowance_deduction.other_deduction
                contract.professional_tax = allowance_deduction.professional_tax
                contract.advance_from_employer = allowance_deduction.advance_from_employer
                contract.provident_fund_loan = allowance_deduction.provident_fund_loan
                contract.overtime = allowance_deduction.overtime
                contract.excessive_leaves = allowance_deduction.excessive_leaves
                contract.arrears = allowance_deduction.arrears
                contract.manual_eobi = allowance_deduction.manual_eobi
            else:
                # Set to 0.0 if no allowance deduction record is found
                contract.pf_employee_contribution = 0.0
                contract.pf_employer_contribution = 0.0
                contract.food_employee_contribution = 0.0
                contract.food_employer_contribution = 0.0
                contract.other_allowance = 0.0
                contract.other_deduction = 0.0
                contract.professional_tax = 0.0
                contract.advance_from_employer = 0.0
                contract.provident_fund_loan = 0.0
                contract.overtime = 0.0
                contract.excessive_leaves = 0.0
                contract.arrears = 0.0
                contract.manual_eobi = 0.0


class HR_Employee(models.Model):
    _inherit = 'hr.employee'

    cnic_exp_date = fields.Date(string='CNIC Expiry Date')
    identification_expiry = fields.Date(string='Identification Expiry Date')
    probation_end_date = fields.Date(string='Probation End Date')
    contract_type = fields.Many2one('hr.contract.type', compute='_compute_contract_type', string='Contract Type', readonly=True)

    @api.depends('employee_id')
    def _compute_contract_type(self):
        for employee in self:
            current_contract = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
            employee.contract_type = current_contract.contract_type_id if current_contract else False









def action_payslip_done(self):
    invalid_payslips = self.filtered(lambda p: p.contract_id and (p.contract_id.date_start > p.date_to or (p.contract_id.date_end and p.contract_id.date_end < p.date_from)))
    if invalid_payslips:
        raise ValidationError(_('The following employees have a contract outside of the payslip period:\n%s', '\n'.join(invalid_payslips.mapped('employee_id.name'))))
    if any(slip.contract_id.state == 'cancel' for slip in self):
        raise ValidationError(_('You cannot validate a payslip on which the contract is cancelled'))
    if any(slip.state == 'cancel' for slip in self):
        raise ValidationError(_("You can't validate a cancelled payslip."))
    self.write({'state' : 'done'})

    line_values = self._get_line_values(['NET'])

    self.filtered(lambda p: not p.credit_note and line_values['NET'][p.id]['total'] < 0).write({'has_negative_net_to_report': True})
    self.mapped('payslip_run_id').action_close()
    # Validate work entries for regular payslips (exclude end of year bonus, ...)
    regular_payslips = self.filtered(lambda p: p.struct_id.type_id.default_struct_id == p.struct_id)
    work_entries = self.env['hr.work.entry']
    for regular_payslip in regular_payslips:
        work_entries |= self.env['hr.work.entry'].search([
            ('date_start', '<=', regular_payslip.date_to),
            ('date_stop', '>=', regular_payslip.date_from),
            ('employee_id', '=', regular_payslip.employee_id.id),
        ])
    # raise UserError(str(work_entries))
    if work_entries:
        work_entries.action_validate()

    if self.env.context.get('payslip_generate_pdf'):
        if self.env.context.get('payslip_generate_pdf_direct'):
            self._generate_pdf()
        else:
            self.write({'queued_for_pdf': True})
            payslip_cron = self.env.ref('hr_payroll.ir_cron_generate_payslip_pdfs', raise_if_not_found=False)
            if payslip_cron:
                payslip_cron._trigger()

    # New functionality to assign Social Security and EOBI amounts
    for payslip in self:
        social_security_line = payslip.line_ids.filtered(lambda line: line.name == "Social Security")
        eobi_line = payslip.line_ids.filtered(lambda line: line.name == "EOBI Employee Contribution")
        eobi_employer_line = payslip.line_ids.filtered(lambda line: line.name == "EOBI Employer Contribution")
        
        # # New error handling for missing lines
        # if not social_security_line:
        #     raise UserError(_('Social Security line not found for employee %s.') % payslip.employee_id.name)
        # if not eobi_line:
        #     raise UserError(_('EOBI line not found for employee %s.') % payslip.employee_id.name)

        social_security_amount = social_security_line.total
        eobi_amount = eobi_line.total
        eobi_employer_amount = eobi_employer_line.total

        # Use the payslip's month and year for the search
        allowance_deduction = self.env['allowances.deduction'].search([
            ('employee_id', '=', payslip.employee_id.id),
            ('month', '=', datetime.strptime(str(payslip.date_from.month), '%m').strftime('%B').lower()),
            ('year', '=', payslip.date_from.year)
        ], limit=1)
        
        # Assign the amounts to ss_employer_contribution and eobi_employer_contribution
        allowance_deduction.ss_employer_contribution = social_security_amount
        allowance_deduction.eobi_contribution = eobi_amount
        allowance_deduction.eobi_employer_contribution = eobi_employer_amount

BaseHrPayslip.action_payslip_done = action_payslip_done






class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # def _action_create_account_move(self):
    #     precision = self.env['decimal.precision'].precision_get('Payroll')

    #     # Add payslip without run
    #     payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

    #     # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
    #     payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
    #     for run in payslip_runs:
    #         if run._are_payslips_ready():
    #             payslips_to_post |= run.slip_ids
    #     raise UserError(str(payslip_runs))
    #     # A payslip need to have a done state and not an accounting move.
    #     payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

    #     # Check that a journal exists on all the structures
    #     if any(not payslip.struct_id for payslip in payslips_to_post):
    #         raise ValidationError(_('One of the contract for these payslips has no structure type.'))
    #     if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
    #         raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        
    #     # Map all payslips by structure journal and pay slips month.
    #     # {'journal_id': {'month': [slip_ids]}}
    #     slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
    #     for slip in payslips_to_post:
    #         raise UserError(f"{slip.struct_id.journal_id.id} == {slip.date or fields.Date().end_of(slip.date_to, 'month')} == {slip}")
    #         slip_mapped_data[slip.struct_id.journal_id.id][slip.date or fields.Date().end_of(slip.date_to, 'month')] |= slip
    #     for journal_id in slip_mapped_data: # For each journal_id.
    #         for slip_date in slip_mapped_data[journal_id]: # For each month.
    #             line_ids = []
    #             debit_sum = 0.0
    #             credit_sum = 0.0
    #             date = slip_date
    #             move_dict = {
    #                 'narration': '',
    #                 'ref': fields.Date().end_of(slip.date_to, 'month').strftime('%B %Y'),
    #                 'journal_id': journal_id,
    #                 'date': date,
    #             }

    #             for slip in slip_mapped_data[journal_id][slip_date]:
    #                 move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
    #                 move_dict['narration'] += Markup('<br/>')
    #                 slip_lines = slip._prepare_slip_lines(date, line_ids)
    #                 line_ids.extend(slip_lines)

    #             for line_id in line_ids: # Get the debit and credit sum.
    #                 debit_sum += line_id['debit']
    #                 credit_sum += line_id['credit']

    #             # The code below is called if there is an error in the balance between credit and debit sum.
    #             if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
    #                 slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
    #             elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
    #                 slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

    #             # Add accounting lines in the move
    #             move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
    #             move = self._create_account_move(move_dict)
    #             for slip in slip_mapped_data[journal_id][slip_date]:
    #                 slip.write({'move_id': move.id, 'date': date})    
    #     return True
    
    # def action_payslip_done(self):
    #     invalid_payslips = self.filtered(lambda p: p.contract_id and (p.contract_id.date_start > p.date_to or (p.contract_id.date_end and p.contract_id.date_end < p.date_from)))
    #     if invalid_payslips:
    #         raise ValidationError(_('The following employees have a contract outside of the payslip period:\n%s', '\n'.join(invalid_payslips.mapped('employee_id.name'))))
    #     if any(slip.contract_id.state == 'cancel' for slip in self):
    #         raise ValidationError(_('You cannot validate a payslip on which the contract is cancelled'))
    #     if any(slip.state == 'cancel' for slip in self):
    #         raise ValidationError(_("You can't validate a cancelled payslip."))
    #     self.write({'state' : 'done'})

    #     line_values = self._get_line_values(['NET'])

    #     self.filtered(lambda p: not p.credit_note and line_values['NET'][p.id]['total'] < 0).write({'has_negative_net_to_report': True})
    #     self.mapped('payslip_run_id').action_close()
    #     # Validate work entries for regular payslips (exclude end of year bonus, ...)
    #     regular_payslips = self.filtered(lambda p: p.struct_id.type_id.default_struct_id == p.struct_id)
    #     work_entries = self.env['hr.work.entry']
    #     for regular_payslip in regular_payslips:
    #         work_entries |= self.env['hr.work.entry'].search([
    #             ('date_start', '<=', regular_payslip.date_to),
    #             ('date_stop', '>=', regular_payslip.date_from),
    #             ('employee_id', '=', regular_payslip.employee_id.id),
    #         ])
    #     if work_entries:
    #         work_entries.action_validate()

    #     if self.env.context.get('payslip_generate_pdf'):
    #         if self.env.context.get('payslip_generate_pdf_direct'):
    #             self._generate_pdf()
    #         else:
    #             self.write({'queued_for_pdf': True})
    #             payslip_cron = self.env.ref('hr_payroll.ir_cron_generate_payslip_pdfs', raise_if_not_found=False)
    #             if payslip_cron:
    #                 payslip_cron._trigger()

    #     # New functionality to assign Social Security and EOBI amounts
    #     for payslip in self:
    #         social_security_line = payslip.line_ids.filtered(lambda line: line.name == "Social Security")
    #         eobi_line = payslip.line_ids.filtered(lambda line: line.name == "EOBI Employee Contribution")
    #         eobi_employer_line = payslip.line_ids.filtered(lambda line: line.name == "EOBI Employer Contribution")
            
    #         # # New error handling for missing lines
    #         # if not social_security_line:
    #         #     raise UserError(_('Social Security line not found for employee %s.') % payslip.employee_id.name)
    #         # if not eobi_line:
    #         #     raise UserError(_('EOBI line not found for employee %s.') % payslip.employee_id.name)

    #         social_security_amount = social_security_line.total
    #         eobi_amount = eobi_line.total
    #         eobi_employer_amount = eobi_employer_line.total

    #         # Use the payslip's month and year for the search
    #         allowance_deduction = self.env['allowances.deduction'].search([
    #             ('employee_id', '=', payslip.employee_id.id),
    #             ('month', '=', datetime.strptime(str(payslip.date_from.month), '%m').strftime('%B').lower()),
    #             ('year', '=', payslip.date_from.year)
    #         ], limit=1)
            
    #         # Assign the amounts to ss_employer_contribution and eobi_employer_contribution
    #         allowance_deduction.ss_employer_contribution = social_security_amount
    #         allowance_deduction.eobi_contribution = eobi_amount
    #         allowance_deduction.eobi_employer_contribution = eobi_employer_amount

