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

class SalarySummaryReport(models.TransientModel):
    _name = 'salary.summary.report'
    _description = 'Salary Summary Report'

    date_from = fields.Date(string='Date From', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=lambda self: date.today())

    

    def action_generate_summary_report_pdf(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both 'Date From' and 'Date To' before generating the report."))

        # Initialize JSON data structure
        report_data = {
            'title': 'Payroll Report',
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'parent_departments': []
        }

        # Initialize models
        payslip_model = self.env['hr.payslip']
        payslip_line_model = self.env['hr.payslip.line']
        
        # Get parent departments (master departments)
        parent_depts = self.env['hr.department'].search([('parent_id', '=', False)], order='name asc')
        
        # Iterate through parent departments
        for parent in parent_depts:
            parent_data = {
                'name': parent.name.upper(),
                'departments': []
            }
            
            # Get child departments for this parent
            departments = self.env['hr.department'].search([('parent_id', '=', parent.id)], order='name asc')
            
            for dept in departments:
                employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='grade_id asc')
                if not employees:
                    continue

                dept_data = {
                    'name': dept.name.upper(),
                    'categories': [],
                    'subtotals': {}
                }

                # Aggregate data by employee category
                category_data = {}
                for emp in employees:
                    payslips = payslip_model.search([
                        ('employee_id', '=', emp.id),
                        ('date_from', '>=', self.date_from),
                        ('date_to', '<=', self.date_to)
                    ])
                    line_amounts = {}
                    for payslip in payslips:
                        payslip_lines = payslip_line_model.search([('slip_id', '=', payslip.id)])
                        for line in payslip_lines:
                            if line.name:
                                line_amounts[line.name] = line_amounts.get(line.name, 0.0) + line.total

                    category = emp.employee_category.name or 'Uncategorized'
                    if category not in category_data:
                        category_data[category] = {
                            'salary_as_on': 0.0, 'increment': 0.0, 'salary_wef': 0.0,
                            'basic_pay': 0.0, 'hr_allow': 0.0, 'conv_allow': 0.0, 'util_allow': 0.0,
                            'med_allow': 0.0, 'other_allow': 0.0, 'arrears': 0.0, 'overtime': 0.0, 'gross': 0.0,
                            'income_tax': 0.0, 'provident_fund': 0.0, 'eobi': 0.0, 'food_charges': 0.0,
                            'advance': 0.0, 'extra_leaves': 0.0, 'prof_tax': 0.0, 'total_ded': 0.0, 'net_salary': 0.0
                        }

                    category_data[category]['salary_as_on'] += emp.contract_id.wage or 0.0
                    category_data[category]['increment'] += emp.contract_id.increment or 0.0
                    category_data[category]['salary_wef'] += (emp.contract_id.wage + emp.contract_id.increment) or 0.0
                    category_data[category]['basic_pay'] += round(line_amounts.get('Basic Salary', 0.0), 2)
                    category_data[category]['hr_allow'] += round(line_amounts.get('House Rent Allowance', 0.0), 2)
                    category_data[category]['conv_allow'] += round(line_amounts.get('Conveyance Allowance', 0.0), 2)
                    category_data[category]['util_allow'] += round(line_amounts.get('Utilities Allowance', 0.0), 2)
                    category_data[category]['med_allow'] += round(line_amounts.get('Medical Allowance', 0.0), 2)
                    category_data[category]['other_allow'] += round(line_amounts.get('Other Allowance', 0.0), 2)
                    category_data[category]['arrears'] += round(line_amounts.get('Arrears', 0.0), 2)
                    category_data[category]['overtime'] += round(line_amounts.get('Overtime', 0.0), 2)
                    category_data[category]['gross'] += round(line_amounts.get('Gross', 0.0), 2)
                    category_data[category]['income_tax'] += round(line_amounts.get('Income Tax', 0.0), 2)
                    category_data[category]['provident_fund'] += round(line_amounts.get('Provident Fund', 0.0), 2)
                    category_data[category]['eobi'] += round(line_amounts.get('EOBI', 0.0), 2)
                    category_data[category]['food_charges'] += round(line_amounts.get('Food Charges', 0.0), 2)
                    category_data[category]['advance'] += round(line_amounts.get('Advance', 0.0), 2)
                    category_data[category]['extra_leaves'] += round(line_amounts.get('Excess Leaves', 0.0), 2)
                    category_data[category]['prof_tax'] += round(line_amounts.get('Professional Tax', 0.0), 2)
                    category_data[category]['total_ded'] += (
                        round(line_amounts.get('Income Tax', 0.0), 2) +
                        round(line_amounts.get('Provident Fund', 0.0), 2) +
                        round(line_amounts.get('EOBI', 0.0), 2) +
                        round(line_amounts.get('Food Charges', 0.0), 2) +
                        round(line_amounts.get('Advance', 0.0), 2) +
                        round(line_amounts.get('Excess Leaves', 0.0), 2) +
                        round(line_amounts.get('Professional Tax', 0.0), 2)
                    )
                    payslip_emp = payslip_model.search([('employee_id', '=', emp.id), ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)], limit=1)
                    category_data[category]['net_salary'] += round(payslip_emp.net_wage if payslip_emp else 0.0, 2)

                # Add category data to department
                serial_no = 1
                for category, data in category_data.items():
                    dept_data['categories'].append({
                        'serial_no': serial_no,
                        'name': category,
                        **data
                    })
                    serial_no += 1

                # Calculate department subtotals
                dept_data['subtotals'] = {
                    'salary_as_on': sum(d['salary_as_on'] for d in category_data.values()),
                    'increment': sum(d['increment'] for d in category_data.values()),
                    'salary_wef': sum(d['salary_wef'] for d in category_data.values()),
                    'basic_pay': sum(d['basic_pay'] for d in category_data.values()),
                    'hr_allow': sum(d['hr_allow'] for d in category_data.values()),
                    'conv_allow': sum(d['conv_allow'] for d in category_data.values()),
                    'util_allow': sum(d['util_allow'] for d in category_data.values()),
                    'med_allow': sum(d['med_allow'] for d in category_data.values()),
                    'other_allow': sum(d['other_allow'] for d in category_data.values()),
                    'arrears': sum(d['arrears'] for d in category_data.values()),
                    'overtime': sum(d['overtime'] for d in category_data.values()),
                    'gross': sum(d['gross'] for d in category_data.values()),
                    'income_tax': sum(d['income_tax'] for d in category_data.values()),
                    'provident_fund': sum(d['provident_fund'] for d in category_data.values()),
                    'eobi': sum(d['eobi'] for d in category_data.values()),
                    'food_charges': sum(d['food_charges'] for d in category_data.values()),
                    'advance': sum(d['advance'] for d in category_data.values()),
                    'extra_leaves': sum(d['extra_leaves'] for d in category_data.values()),
                    'prof_tax': sum(d['prof_tax'] for d in category_data.values()),
                    'total_ded': sum(d['total_ded'] for d in category_data.values()),
                    'net_salary': sum(d['net_salary'] for d in category_data.values())
                }
                parent_data['departments'].append(dept_data)
            
            # Only add parent department if it has departments with data
            if parent_data['departments']:
                report_data['parent_departments'].append(parent_data)

        return self.env.ref('payroll_salary_summary_report.action_summary_report_pdf').report_action(self, data={'report_data': report_data})
        raise UserError(str(report_data))