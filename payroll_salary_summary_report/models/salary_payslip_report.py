import io
import xlsxwriter
import base64
from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta, date
from odoo import api, fields, models
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
from datetime import timedelta

import ast

class SalaryPayslipReport(models.TransientModel):
    _name = 'salary.payslip.report'
    _description = 'Salary Payslip Report'

    date_from = fields.Date(string='Date From', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=lambda self: date.today())
    employee_ids = fields.Many2many('hr.employee', string='Employees', help="Select employees to include in the report.")
    department_ids = fields.Many2many('hr.department', string='Departments', help="Select departments to include in the report.")

    
    def action_generate_payslip_report_pdf(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both 'Date From' and 'Date To' before generating the report."))

        # Initialize JSON data structure
        report_data = {
            'title': 'Salary Slip',
            'month': self.date_from.strftime('%b %Y'),
            'slips': []
        }

        # Initialize models
        payslip_model = self.env['hr.payslip']
        payslip_line_model = self.env['hr.payslip.line']

        # Get employees based on selection
        emp_domain = []
        if self.employee_ids:
            emp_domain.append(('id', 'in', self.employee_ids.ids))
        if self.department_ids:
            emp_domain.append(('department_id', 'in', self.department_ids.ids))
        employees = self.env['hr.employee'].search(emp_domain) if emp_domain else self.env['hr.employee'].search([])

        employee_counter = 1  # Initialize counter to track employee number

        # Iterate over the employees in pairs
        for i in range(0, len(employees), 2):  # Step by 2 to process pairs
            slip_data_pair = {
                'employee_no_1': '',
                'name_1': '',
                'designation_1': '',
                'account_no_1': '',
                'pay_allowances_1': [],
                'deductions_1': [],
                'gross_1': 0.0,
                'total_deduction_1': 0.0,
                'net_salary_1': 0.0,
                'employee_no_2': '',
                'name_2': '',
                'designation_2': '',
                'account_no_2': '',
                'pay_allowances_2': [],
                'deductions_2': [],
                'gross_2': 0.0,
                'total_deduction_2': 0.0,
                'net_salary_2': 0.0
            }

            # Define fields as per the provided salary slip
            allowance_fields = [
                ('Basic Salary', 'basic_pay'),
                ('House Rent Allowance', 'hr_allow'),
                ('Utilities Allowance', 'util_allow'),
                ('Medical Allowance', 'med_allow'),
                ('Arrears', 'arrears'),
                ('Other Allowance', 'other_allow'),
                ('Food Charges Contribution', 'food_charges_contrib'),
                ('Overtime', 'overtime')
            ]
            deduction_fields = [
                ('Income Tax', 'income_tax'),
                ('Provident Fund', 'provident_fund'),
                ('Provident Fund Loan', 'pf_loan'),
                ('EOBI', 'eobi'),
                ('Food Charges', 'food_charges'),
                ('Advance', 'advance'),
                ('Excess Leaves', 'extra_leaves'),
                ('Professional Tax', 'prof_tax'),
                ('Others', 'others')
            ]

            # Ensure there is a second employee in the pair, otherwise just process the single employee
            emp_1 = employees[i]
            emp_2 = employees[i + 1] if i + 1 < len(employees) else None

            # Get payslip for the first employee
            payslip_1 = payslip_model.search([
                ('employee_id', '=', emp_1.id),
                ('date_from', '>=', self.date_from),
                ('date_to', '<=', self.date_to)
            ], limit=1)
            # raise UserError(['Payslip_1:', str(payslip_1)])

            if payslip_1:
                # Initialize slip data for employee 1
                payslip_lines_1 = payslip_line_model.search([('slip_id', '=', payslip_1.id)])
                line_amounts_1 = {line.name: line.total for line in payslip_lines_1 if line.name}

                # Populate allowances for employee 1
                for field_name, key in allowance_fields:
                    amount = round(line_amounts_1.get(field_name, 0.0), 2)
                    slip_data_pair['pay_allowances_1'].append({
                        'name': field_name,
                        'amount': amount
                    })
                    if field_name == 'Gross':
                        slip_data_pair['gross_1'] = amount
                    else:
                        slip_data_pair['gross_1'] += amount

                # Populate deductions for employee 1
                for field_name, key in deduction_fields:
                    amount = round(line_amounts_1.get(field_name, 0.0), 2)
                    slip_data_pair['deductions_1'].append({
                        'name': field_name,
                        'amount': amount
                    })
                    slip_data_pair['total_deduction_1'] += amount

                # Calculate net salary for employee 1
                slip_data_pair['net_salary_1'] = round(payslip_1.net_wage or 0.0, 2)

                # Fill in other details for employee 1
                slip_data_pair['employee_no_1'] = emp_1.employee_id or ''
                slip_data_pair['name_1'] = emp_1.name or ''
                slip_data_pair['designation_1'] = emp_1.job_id.name or ''
                slip_data_pair['account_no_1'] = emp_1.bank_account_id.acc_number or ''

            # If there is a second employee in the pair, do the same for them
            if emp_2:
                payslip_2 = payslip_model.search([
                    ('employee_id', '=', emp_2.id),
                    ('date_from', '>=', self.date_from),
                    ('date_to', '<=', self.date_to)
                ], limit=1)

                # raise UserError(['Payslip_1:', str(payslip_1), 'Payslip_2:', str(payslip_2)])

                if payslip_2:
                    # Initialize slip data for employee 2
                    payslip_lines_2 = payslip_line_model.search([('slip_id', '=', payslip_2.id)])
                    line_amounts_2 = {line.name: line.total for line in payslip_lines_2 if line.name}

                    # Populate allowances for employee 2
                    for field_name, key in allowance_fields:
                        amount = round(line_amounts_2.get(field_name, 0.0), 2)
                        slip_data_pair['pay_allowances_2'].append({
                            'name': field_name,
                            'amount': amount
                        })
                        if field_name == 'Gross':
                            slip_data_pair['gross_2'] = amount
                        else:
                            slip_data_pair['gross_2'] += amount

                    # Populate deductions for employee 2
                    for field_name, key in deduction_fields:
                        amount = round(line_amounts_2.get(field_name, 0.0), 2)
                        slip_data_pair['deductions_2'].append({
                            'name': field_name,
                            'amount': amount
                        })
                        slip_data_pair['total_deduction_2'] += amount

                    # Calculate net salary for employee 2
                    slip_data_pair['net_salary_2'] = round(payslip_2.net_wage or 0.0, 2)

                    # Fill in other details for employee 2
                    slip_data_pair['employee_no_2'] = emp_2.employee_id or ''
                    slip_data_pair['name_2'] = emp_2.name or ''
                    slip_data_pair['designation_2'] = emp_2.job_id.name or ''
                    slip_data_pair['account_no_2'] = emp_2.bank_account_id.acc_number or ''

            # Append the combined slip data for this pair of employees
            report_data['slips'].append(slip_data_pair)



        return self.env.ref('payroll_salary_summary_report.action_payslip_report_pdf').report_action(self, data={'report_data': report_data})
        raise UserError(str(report_data))
