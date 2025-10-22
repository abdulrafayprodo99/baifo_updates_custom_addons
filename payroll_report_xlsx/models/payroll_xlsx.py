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

class PayrollReport(models.TransientModel):
    _name = 'payroll.report'
    _description = 'Payroll Report'

    excel_file = fields.Binary(string="Excel File")
    date_from = fields.Date(string='Date From', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=lambda self: date.today())

    
    pdf_file = fields.Binary("PDF Report")
    pdf_filename = fields.Char("PDF Filename")




    def sort_departments_asc(self, departments):
        return sorted(departments, 
                    key=lambda x: (
                        x['master_department_id'][0] if x['master_department_id'] else float('inf'),
                        x['name']
                    ))
    

    def sort_employee_data(self, employee_data_list, sort_by='sr_no'):
        """
        Sorts the employee data list based on the given argument.

        Args:
            employee_data_list (list): List of employee data dictionaries.
            sort_by (str): The field by which to sort. Default is 'employee_code'.
        
        Returns:
            list: Sorted employee data list.
        """
        return sorted(employee_data_list, key=lambda x: x.get(sort_by, ''))
    
    
    def action_generate_report_pdf(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both 'Date From' and 'Date To' before generating the JSON report."))

        # Initialize the JSON structure
        report_data = {
            'report_title': 'Payroll Report',
            'date_from': self.date_from.strftime('%Y-%m-%d'),
            'date_to': self.date_to.strftime('%Y-%m-%d'),
            'departments': []
        }

        # Fetch departments and sort
        departments = self.env['hr.department'].search([], order='master_department_id asc, name asc')

        for dept in departments:
            employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='grade_id asc')
            # Fetch employees sorted by employee_id
            # employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='employee_id asc')
            # Fetch employees without sorting


            # employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='x_studio_sort_id asc')
            
            if not employees:
                continue

            dept_data = {
                'department_name': dept.name,
                'employees': []
            }

            for emp in employees:
                payslips = self.env['hr.payslip'].search([
                    # ('employee_code', '=', emp.employee_id),
                    ('employee_id', '=', emp.id),
                    ('date_from', '>=', self.date_from),
                    ('date_to', '<=', self.date_to)
                ])
                attendances = self.env['import.attendance'].search([
                    ('employee_id', '=', emp.id)
                ])

                line_amounts = {}
                for payslip in payslips:
                    payslip_lines = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id)])
                    for line in payslip_lines:
                        if line.name:
                            line_amounts[line.name] = line_amounts.get(line.name, 0.0) + line.total

                total_deductions = (
                    line_amounts.get('Income Tax', 0.0) +
                    line_amounts.get('Provident Fund', 0.0) +
                    line_amounts.get('EOBI', 0.0) +
                    line_amounts.get('Food Charges', 0.0) +
                    line_amounts.get('Advance', 0.0) +
                    line_amounts.get('Provident Fund Loan', 0.0) +
                    line_amounts.get('Professional Tax', 0.0) +
                    line_amounts.get('Excess Leaves', 0.0)
                )

                payslip_emp = self.env['hr.payslip'].search([
                    ('employee_id', '=', emp.id)
                ], limit=1)
                net_salary = payslip_emp.net_wage if payslip_emp else 0.0

                employee_data = {
                    'serial_no': len(dept_data['employees']) + 1,
                    'employee_code': emp.employee_id or '',
                    'name': emp.name or '',
                    'sr_no': emp.x_studio_sort_id or '',
                    'designation': emp.job_id.name or '',
                    'contract_type': emp.contract_type.name or '',
                    'employee_category': emp.employee_category.name or '',
                    'no_of_days': attendances.present_days if attendances else 0,
                    'salary_as_on': emp.contract_id.wage or 0.0,
                    'increment': emp.contract_id.increment or 0.0,
                    'salary_wef': (emp.contract_id.wage or 0.0) + (emp.contract_id.increment or 0.0),
                    'pay_and_allowances': {
                        'basic_pay': line_amounts.get('Basic Salary', 0.0),
                        'house_rent_allowance': line_amounts.get('House Rent Allowance', 0.0),
                        'conveyance_allowance': line_amounts.get('Conveyance Allowance', 0.0),
                        'utilities_allowance': line_amounts.get('Utilities Allowance', 0.0),
                        'medical_allowance': line_amounts.get('Medical Allowance', 0.0),
                        'other_allow': line_amounts.get('Other Allowance', 0.0),
                        'arrears': line_amounts.get('Arrears', 0.0),
                        'overtime_driver_allowance': line_amounts.get('Overtime', 0.0),
                        'gross_pay': line_amounts.get('Gross',0.0)
                        # 'gross_pay': sum(line_amounts.values())
                    },
                    'deductions': {
                        'income_tax': line_amounts.get('Income Tax', 0.0),
                        'provident_fund': line_amounts.get('Provident Fund', 0.0),
                        'eobi': line_amounts.get('EOBI', 0.0),
                        'food_charges': line_amounts.get('Food Charges', 0.0),
                        'advance': line_amounts.get('Advance', 0.0),
                        'provident_fund_loan': line_amounts.get('Provident Fund Loan', 0.0),
                        'professional_tax': line_amounts.get('Professional Tax', 0.0),
                        'excess_leaves': line_amounts.get('Excess Leaves', 0.0),
                        'total_deduction': total_deductions
                    },
                    'net_salary': net_salary,
                    'account_no': emp.bank_account_id.acc_number if emp.bank_account_id and emp.bank_account_id.acc_number else '',
                    'remarks': '',
                    'cost_centre': f"[{emp.contract_id.analytic_account_id.code}] {emp.contract_id.analytic_account_id.name}" 
                        if emp.contract_id and emp.contract_id.analytic_account_id else '',
                    'department': emp.department_id.name or ''
                }
                dept_data['employees'].append(employee_data)

                # dept_data['employees'] = self.sort_employee_data(dept_data['employees'], sort_by='employee_code')
                dept_data['employees'] = self.sort_employee_data(dept_data['employees'], sort_by='sr_no')

            report_data['departments'].append(dept_data)
            # raise UserError(str(report_data))
        
        return self.env.ref('payroll_report_xlsx.action_report_payroll_pdf').report_action(self, data={'report_data': report_data})


    # def action_generate_report_excel(self):
    #     if not self.date_from or not self.date_to:
    #         raise UserError(_("Please set both 'Date From' and 'Date To' before generating the report."))

    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output)
    #     worksheet = workbook.add_worksheet('Payroll Report')

    #     # Define formats (unchanged)
    #     bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#A3C1AD', 'font_size': 15})
    #     normal = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 15})
    #     number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 15, 'num_format': '#,##0'})
    #     merge_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D3D3D3', 'font_size': 15})
    #     dept_format = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter', 'bg_color': '#B6D7A8', 'border': 1, 'font_size': 15})
    #     subtotal_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#FFFACD', 'font_size': 15})
    #     grand_total_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#FFD700', 'font_size': 15})

    #     # Set column widths based on headers (unchanged)
    #     column_widths = {col: len(header) for col, header in enumerate([
    #         "S.NO", "EMP. CODE", "NAME", "DESIGNATION", "CONTRACT TYPE",
    #         "EMPLOYEE CATEGORY", "NO. OF DAYS",
    #         f"SALARY AS ON {self.date_from - timedelta(days=1):%d-%m-%Y}",
    #         "INCREMENT/SALARY ADJUSTMENT", f"SALARY W.E.F. {self.date_from}",
    #         "BASIC PAY", "HR ALLOW", "CONV. ALLOW", "UTILITIES ALLOW",
    #         "MEDICAL ALLOW", "ARREARS/OTHERS", "OVERTIME/DRIVER ALLOW", "GROSS PAY",
    #         "INCOME TAX", "PROVIDENT FUND", "EOBI", "FOOD CHARGES", "ADVANCE",
    #         "Provident Fund Loan", "PROFESSIONAL TAX", "EXCESS LEAVES", "TOTAL DEDUCTION", "NET SALARY",
    #         "ACCOUNT NO", "REMARKS", "COST CENTRE", "DEPT"
    #     ])}

    #     # Set column widths and merge cells for title (unchanged)
    #     worksheet.set_column(0, 27, 15)
    #     worksheet.merge_range('A1:AE1', 'Payroll Report', merge_format)
    #     worksheet.merge_range('A2:AE2', f'Report Date: {self.date_from} to {self.date_to}', merge_format)

    #     # Define headers (unchanged)
    #     headers = [
    #         "S.NO", "EMP. CODE", "NAME", "DESIGNATION", "CONTRACT TYPE",
    #         "EMPLOYEE CATEGORY", "NO. OF DAYS",
    #         f"SALARY AS ON {self.date_from - timedelta(days=1):%d-%m-%Y}",
    #         "INCREMENT/SALARY ADJUSTMENT", f"SALARY W.E.F. {self.date_from}",
    #         "BASIC PAY", "HR ALLOW", "CONV. ALLOW", "UTILITIES ALLOW",
    #         "MEDICAL ALLOW", "ARREARS/OTHERS", "OVERTIME/DRIVER ALLOW", "GROSS PAY",
    #         "INCOME TAX", "PROVIDENT FUND", "EOBI", "FOOD CHARGES", "ADVANCE",
    #         "Provident Fund Loan", "PROFESSIONAL TAX", "EXCESS LEAVES", "TOTAL DEDUCTION", "NET SALARY",
    #         "ACCOUNT NO", "REMARKS", "COST CENTRE", "DEPT"
    #     ]

    #     # Initialize models and departments (unchanged)
    #     payslip_model = self.env['hr.payslip']
    #     payslip_line_model = self.env['hr.payslip.line']
    #     departments = self.env['hr.department'].search([], order='master_department_id asc, name asc')

    #     # Set page layout (unchanged)
    #     worksheet.set_paper(9)
    #     worksheet.set_landscape()
    #     worksheet.set_margins(0.2, 0.2, 0.2, 0.2)
    #     worksheet.set_print_scale(100)
    #     worksheet.set_default_row(35)
    #     worksheet.fit_to_pages(1, 0)

    #     row = 3
    #     serial_no = 1
    #     row_list = []
    #     grand_totals = {
    #         'no_of_days': 0, 'salary_as_on': 0, 'increment': 0, 'salary_wef': 0,
    #         'basic_pay': 0, 'hr_allow': 0, 'conv_allow': 0, 'util_allow': 0,
    #         'med_allow': 0, 'arrears': 0, 'overtime': 0, 'gross_pay': 0,
    #         'income_tax': 0, 'prov_fund': 0, 'eobi': 0, 'food_charges': 0,
    #         'advance': 0, 'pf_loan': 0, 'prof_tax': 0, 'excess_leaves': 0,
    #         'total_deduction': 0, 'net_salary': 0
    #     }

    #     # Iterate through departments
    #     for dept in departments:
    #         employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='grade_id asc')
    #         if not employees:
    #             continue

    #         # Initialize department totals (unchanged)
    #         dept_totals = {
    #             'no_of_days': 0, 'salary_as_on': 0, 'increment': 0, 'salary_wef': 0,
    #             'basic_pay': 0, 'hr_allow': 0, 'conv_allow': 0, 'util_allow': 0,
    #             'med_allow': 0, 'arrears': 0, 'overtime': 0, 'gross_pay': 0,
    #             'income_tax': 0, 'prov_fund': 0, 'eobi': 0, 'food_charges': 0,
    #             'advance': 0, 'pf_loan': 0, 'prof_tax': 0, 'excess_leaves': 0,
    #             'total_deduction': 0, 'net_salary': 0
    #         }

    #         # Write department header and column headers (unchanged)
    #         worksheet.merge_range(row, 0, row, 3, f"Department: {dept.name}", dept_format)
    #         worksheet.write(row + 1, 0, headers[0], bold)
    #         worksheet.write(row + 1, 1, headers[1], bold)
    #         worksheet.write(row + 1, 2, headers[2], bold)
    #         worksheet.write(row + 1, 3, headers[3], bold)
    #         worksheet.write(row + 1, 4, headers[4], bold)
    #         worksheet.write(row + 1, 5, headers[5], bold)
    #         worksheet.write(row + 1, 6, headers[6], bold)
    #         worksheet.write(row + 1, 7, headers[7], bold)
    #         worksheet.write(row + 1, 8, headers[8], bold)
    #         worksheet.write(row + 1, 9, headers[9], bold)
    #         worksheet.merge_range(row + 1, 10, row + 1, 16, 'Pay and Allowance', merge_format)
    #         worksheet.write(row + 2, 10, headers[10], merge_format)
    #         worksheet.write(row + 2, 11, headers[11], merge_format)
    #         worksheet.write(row + 2, 12, headers[12], merge_format)
    #         worksheet.write(row + 2, 13, headers[13], merge_format)
    #         worksheet.write(row + 2, 14, headers[14], merge_format)
    #         worksheet.write(row + 2, 15, headers[15], merge_format)
    #         worksheet.write(row + 2, 16, headers[16], merge_format)
    #         worksheet.write(row + 1, 17, headers[17], bold)
    #         worksheet.merge_range(row + 1, 18, row + 1, 25, 'Deduction', merge_format)
    #         worksheet.write(row + 2, 18, headers[18], merge_format)
    #         worksheet.write(row + 2, 19, headers[19], merge_format)
    #         worksheet.write(row + 2, 20, headers[20], merge_format)
    #         worksheet.write(row + 2, 21, headers[21], merge_format)
    #         worksheet.write(row + 2, 22, headers[22], merge_format)
    #         worksheet.write(row + 2, 23, headers[23], merge_format)
    #         worksheet.write(row + 2, 24, headers[24], merge_format)
    #         worksheet.write(row + 2, 25, headers[25], merge_format)
    #         worksheet.write(row + 1, 26, headers[26], bold)
    #         worksheet.write(row + 1, 27, headers[27], bold)
    #         worksheet.write(row + 1, 28, headers[28], bold)
    #         worksheet.write(row + 1, 29, headers[29], bold)
    #         worksheet.write(row + 1, 30, headers[30], bold)
    #         worksheet.write(row + 1, 31, headers[31], bold)

    #         row += 3

    #         # Collect employee data
    #         employee_data_list = []
    #         for emp in employees:
    #             payslips = payslip_model.search([
    #                 ('employee_id', '=', emp.id),
    #                 ('date_from', '>=', self.date_from),
    #                 ('date_to', '<=', self.date_to)
    #             ])

    #             attendances = self.env['import.attendance'].search([
    #                 ('employee_id', '=', emp.id)
    #             ])
    #             line_amounts = {}
    #             for payslip in payslips:
    #                 payslip_lines = payslip_line_model.search([('slip_id', '=', payslip.id)])
    #                 for line in payslip_lines:
    #                     if line.name:
    #                         line_amounts[line.name] = line_amounts.get(line.name, 0.0) + line.total

    #             # Calculate total deductions
    #             total_deductions = (
    #                 line_amounts.get('Income Tax', 0.0) +
    #                 line_amounts.get('Provident Fund', 0.0) +
    #                 line_amounts.get('EOBI', 0.0) +
    #                 line_amounts.get('Food Charges', 0.0) +
    #                 line_amounts.get('Advance', 0.0) +
    #                 line_amounts.get('Provident Fund Loan', 0.0) +
    #                 line_amounts.get('Professional Tax', 0.0) +
    #                 line_amounts.get('Excess Leaves', 0.0)
    #             )

    #             # Get net salary
    #             payslip_emp = payslip_model.search([('employee_id', '=', emp.id), ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)], limit=1)
    #             net_salary = payslip_emp.net_wage if payslip_emp else 0.0

    #             # Store employee data
    #             employee_data = {
    #                 'sr_no': serial_no,
    #                 'sort_id': emp.x_studio_sort_id or '',
    #                 'employee_code': emp.employee_id or '',
    #                 'name': emp.name or '',
    #                 'designation': emp.job_id.name or '',
    #                 'contract_type': emp.contract_type.name or '',
    #                 'employee_category': emp.employee_category.name or '',
    #                 'no_of_days': attendances.present_days if attendances else 0,
    #                 'salary_as_on': emp.contract_id.wage,
    #                 'increment': emp.contract_id.increment,
    #                 'salary_wef': emp.contract_id.wage + emp.contract_id.increment,
    #                 'basic_pay': round(line_amounts.get('Basic Salary', 0.0), 2),
    #                 'hr_allow': round(line_amounts.get('House Rent Allowance', 0.0), 2),
    #                 'conv_allow': round(line_amounts.get('Conveyance Allowance', 0.0), 2),
    #                 'util_allow': round(line_amounts.get('Utilities Allowance', 0.0), 2),
    #                 'med_allow': round(line_amounts.get('Medical Allowance', 0.0), 2),
    #                 'arrears': round(line_amounts.get('Other Allowance', 0.0), 2),
    #                 'overtime': round(line_amounts.get('Overtime', 0.0), 2),
    #                 'gross_pay': round(line_amounts.get('Gross', 0.0), 2),
    #                 'income_tax': round(line_amounts.get('Income Tax', 0.0), 2),
    #                 'prov_fund': round(line_amounts.get('Provident Fund', 0.0), 2),
    #                 'eobi': round(line_amounts.get('EOBI', 0.0), 2),
    #                 'food_charges': round(line_amounts.get('Food Charges', 0.0), 2),
    #                 'advance': round(line_amounts.get('Advance', 0.0), 2),
    #                 'pf_loan': round(line_amounts.get('Provident Fund Loan', 0.0), 2),
    #                 'prof_tax': round(line_amounts.get('Professional Tax', 0.0), 2),
    #                 'excess_leaves': round(line_amounts.get('Excess Leaves', 0.0), 2),
    #                 'total_deduction': round(total_deductions, 2),
    #                 'net_salary': round(net_salary, 2),
    #                 'account_no': emp.bank_account_id.acc_number if emp.bank_account_id and emp.bank_account_id.acc_number else '',
    #                 'remarks': '',
    #                 'cost_centre': f"[{emp.contract_id.analytic_account_id.code}] {emp.contract_id.analytic_account_id.name}" if emp.contract_id and emp.contract_id.analytic_account_id else '',
    #                 'dept': emp.department_id.name or ''
    #             }
    #             employee_data_list.append(employee_data)
    #             serial_no += 1

    #         # Sort employee data by sr_no
    #         sorted_employee_data = self.sort_employee_data(employee_data_list, sort_by='sort_id')
    #         # raise UserError(str(sorted_employee_data))

    #         # Write sorted employee data to worksheet
    #         count = 0
    #         for emp_data in sorted_employee_data:
    #             count += 1
    #             worksheet.write(row, 0, count, normal)
    #             worksheet.write(row, 1, emp_data['employee_code'], normal)
    #             worksheet.write(row, 2, emp_data['name'], normal)
    #             worksheet.write(row, 3, emp_data['designation'], normal)
    #             worksheet.write(row, 4, emp_data['contract_type'], normal)
    #             worksheet.write(row, 5, emp_data['employee_category'], normal)
    #             worksheet.write(row, 6, emp_data['no_of_days'], normal)
    #             worksheet.write(row, 7, emp_data['salary_as_on'], number_format)
    #             worksheet.write(row, 8, emp_data['increment'], number_format)
    #             worksheet.write(row, 9, emp_data['salary_wef'], number_format)
    #             worksheet.write(row, 10, emp_data['basic_pay'], number_format)
    #             worksheet.write(row, 11, emp_data['hr_allow'], number_format)
    #             worksheet.write(row, 12, emp_data['conv_allow'], number_format)
    #             worksheet.write(row, 13, emp_data['util_allow'], number_format)
    #             worksheet.write(row, 14, emp_data['med_allow'], number_format)
    #             worksheet.write(row, 15, emp_data['arrears'], number_format)
    #             worksheet.write(row, 16, emp_data['overtime'], number_format)
    #             worksheet.write(row, 17, emp_data['gross_pay'], number_format)
    #             worksheet.write(row, 18, emp_data['income_tax'], number_format)
    #             worksheet.write(row, 19, emp_data['prov_fund'], number_format)
    #             worksheet.write(row, 20, emp_data['eobi'], number_format)
    #             worksheet.write(row, 21, emp_data['food_charges'], number_format)
    #             worksheet.write(row, 22, emp_data['advance'], number_format)
    #             worksheet.write(row, 23, emp_data['pf_loan'], number_format)
    #             worksheet.write(row, 24, emp_data['prof_tax'], number_format)
    #             worksheet.write(row, 25, emp_data['excess_leaves'], number_format)
    #             worksheet.write(row, 26, emp_data['total_deduction'], number_format)
    #             worksheet.write(row, 27, emp_data['net_salary'], number_format)
    #             worksheet.write(row, 28, emp_data['account_no'], normal)
    #             worksheet.write(row, 29, emp_data['remarks'], normal)
    #             worksheet.write(row, 30, emp_data['cost_centre'], normal)
    #             worksheet.write(row, 31, emp_data['dept'], normal)

    #             # Update department totals
    #             dept_totals['no_of_days'] += emp_data['no_of_days']
    #             dept_totals['salary_as_on'] += emp_data['salary_as_on']
    #             dept_totals['increment'] += emp_data['increment']
    #             dept_totals['salary_wef'] += emp_data['salary_wef']
    #             dept_totals['basic_pay'] += emp_data['basic_pay']
    #             dept_totals['hr_allow'] += emp_data['hr_allow']
    #             dept_totals['conv_allow'] += emp_data['conv_allow']
    #             dept_totals['util_allow'] += emp_data['util_allow']
    #             dept_totals['med_allow'] += emp_data['med_allow']
    #             dept_totals['arrears'] += emp_data['arrears']
    #             dept_totals['overtime'] += emp_data['overtime']
    #             dept_totals['gross_pay'] += emp_data['gross_pay']
    #             dept_totals['income_tax'] += emp_data['income_tax']
    #             dept_totals['prov_fund'] += emp_data['prov_fund']
    #             dept_totals['eobi'] += emp_data['eobi']
    #             dept_totals['food_charges'] += emp_data['food_charges']
    #             dept_totals['advance'] += emp_data['advance']
    #             dept_totals['pf_loan'] += emp_data['pf_loan']
    #             dept_totals['prof_tax'] += emp_data['prof_tax']
    #             dept_totals['excess_leaves'] += emp_data['excess_leaves']
    #             dept_totals['total_deduction'] += emp_data['total_deduction']
    #             dept_totals['net_salary'] += emp_data['net_salary']


    #             row += 1

    #         # Update grand totals
    #         for key in grand_totals:
    #             grand_totals[key] += dept_totals[key]

    #         # Write department subtotal (unchanged)
    #         worksheet.merge_range(row, 0, row, 3, f"Subtotal for {dept.name}", subtotal_format)
    #         worksheet.write(row, 6, dept_totals['no_of_days'], number_format)
    #         worksheet.write(row, 7, round(dept_totals['salary_as_on'], 2), number_format)
    #         worksheet.write(row, 8, round(dept_totals['increment'], 2), number_format)
    #         worksheet.write(row, 9, round(dept_totals['salary_wef'], 2), number_format)
    #         worksheet.write(row, 10, round(dept_totals['basic_pay'], 2), number_format)
    #         worksheet.write(row, 11, round(dept_totals['hr_allow'], 2), number_format)
    #         worksheet.write(row, 12, round(dept_totals['conv_allow'], 2), number_format)
    #         worksheet.write(row, 13, round(dept_totals['util_allow'], 2), number_format)
    #         worksheet.write(row, 14, round(dept_totals['med_allow'], 2), number_format)
    #         worksheet.write(row, 15, round(dept_totals['arrears'], 2), number_format)
    #         worksheet.write(row, 16, round(dept_totals['overtime'], 2), number_format)
    #         worksheet.write(row, 17, round(dept_totals['gross_pay'], 2), number_format)
    #         worksheet.write(row, 18, round(dept_totals['income_tax'], 2), number_format)
    #         worksheet.write(row, 19, round(dept_totals['prov_fund'], 2), number_format)
    #         worksheet.write(row, 20, round(dept_totals['eobi'], 2), number_format)
    #         worksheet.write(row, 21, round(dept_totals['food_charges'], 2), number_format)
    #         worksheet.write(row, 22, round(dept_totals['advance'], 2), number_format)
    #         worksheet.write(row, 23, round(dept_totals['pf_loan'], 2), number_format)
    #         worksheet.write(row, 24, round(dept_totals['prof_tax'], 2), number_format)
    #         worksheet.write(row, 25, round(dept_totals['excess_leaves'], 2), number_format)
    #         worksheet.write(row, 26, round(dept_totals['total_deduction'], 2), number_format)
    #         worksheet.write(row, 27, round(dept_totals['net_salary'], 2), number_format)

    #         row += 1
    #         worksheet.write(row, 0, '')
    #         row += 1
    #         row_list.append(row)

    #     # Write grand total (unchanged)
    #     worksheet.merge_range(row, 0, row, 3, "Grand Total", grand_total_format)
    #     worksheet.write(row, 6, grand_totals['no_of_days'], number_format)
    #     worksheet.write(row, 7, round(grand_totals['salary_as_on'], 2), number_format)
    #     worksheet.write(row, 8, round(grand_totals['increment'], 2), number_format)
    #     worksheet.write(row, 9, round(grand_totals['salary_wef'], 2), number_format)
    #     worksheet.write(row, 10, round(grand_totals['basic_pay'], 2), number_format)
    #     worksheet.write(row, 11, round(grand_totals['hr_allow'], 2), number_format)
    #     worksheet.write(row, 12, round(grand_totals['conv_allow'], 2), number_format)
    #     worksheet.write(row, 13, round(grand_totals['util_allow'], 2), number_format)
    #     worksheet.write(row, 14, round(grand_totals['med_allow'], 2), number_format)
    #     worksheet.write(row, 15, round(grand_totals['arrears'], 2), number_format)
    #     worksheet.write(row, 16, round(grand_totals['overtime'], 2), number_format)
    #     worksheet.write(row, 17, round(grand_totals['gross_pay'], 2), number_format)
    #     worksheet.write(row, 18, round(grand_totals['income_tax'], 2), number_format)
    #     worksheet.write(row, 19, round(grand_totals['prov_fund'], 2), number_format)
    #     worksheet.write(row, 20, round(grand_totals['eobi'], 2), number_format)
    #     worksheet.write(row, 21, round(grand_totals['food_charges'], 2), number_format)
    #     worksheet.write(row, 22, round(grand_totals['advance'], 2), number_format)
    #     worksheet.write(row, 23, round(grand_totals['pf_loan'], 2), number_format)
    #     worksheet.write(row, 24, round(grand_totals['prof_tax'], 2), number_format)
    #     worksheet.write(row, 25, round(grand_totals['excess_leaves'], 2), number_format)
    #     worksheet.write(row, 26, round(grand_totals['total_deduction'], 2), number_format)
    #     worksheet.write(row, 27, round(grand_totals['net_salary'], 2), number_format)

    #     row += 1

    #     # Set custom column widths (unchanged)
    #     inch_to_width = 7.5
    #     inches_list = [0.6, 1.1, 4.2, 6, 2, 2.2, 1.5, 2.5, 3.3, 2.8, 1.5, 1.5, 2, 2, 1.8, 1.5, 2.6, 1.6, 1.5, 2, 1.5, 1.8, 1.6, 1, 2, 2, 2, 1.5, 3.3, 2, 5.5, 4.5]
    #     added_widths = [inch_to_width * inches for inches in inches_list]

    #     for col in range(len(column_widths)):
    #         worksheet.set_column(col, col, column_widths[col] + added_widths[col])

    #     worksheet.set_h_pagebreaks(row_list)
    #     workbook.close()
    #     output.seek(0)

    #     wizard = self.env['payroll.report'].create({'excel_file': base64.b64encode(output.getvalue())})
    #     output.close()

    #     filename = f'Salary_Report_Grouped_By_Department.xls'

    #     return {
    #         'type': 'ir.actions.act_url',
    #         'name': _("Salary Report"),
    #         'url': f"/web/content/{self._name}/{wizard.id}/excel_file/{filename}?download=true",
    #         'target': 'self'
    #     }

    def action_generate_report_excel(self):
            if not self.date_from or not self.date_to:
                raise UserError(_("Please set both 'Date From' and 'Date To' before generating the report."))

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Payroll Report')

            # Define formats (unchanged)
            bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#A3C1AD', 'font_size': 15})
            normal = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 15})
            number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 15, 'num_format': '#,##0'})
            merge_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D3D3D3', 'font_size': 15})
            dept_format = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter', 'bg_color': '#B6D7A8', 'border': 1, 'font_size': 15})
            subtotal_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#FFFACD', 'font_size': 15})
            grand_total_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#FFD700', 'font_size': 15})

            # Set column widths based on headers
            column_widths = {col: len(header) for col, header in enumerate([
                "S.NO", "EMP. CODE", "NAME", "DESIGNATION", "CONTRACT TYPE",
                "EMPLOYEE CATEGORY", "NO. OF DAYS",
                f"SALARY AS ON {self.date_from - timedelta(days=1):%d-%m-%Y}",
                "INCREMENT/SALARY ADJUSTMENT", f"SALARY W.E.F. {self.date_from}",
                "BASIC PAY", "HR ALLOW", "CONV. ALLOW", "UTILITIES ALLOW",
                "MEDICAL ALLOW", "OTHER ALLOWANCES", "ARREARS", "OVERTIME/DRIVER ALLOW", "GROSS PAY",
                "INCOME TAX", "PROVIDENT FUND", "EOBI", "FOOD CHARGES", "ADVANCE",
                "Provident Fund Loan", "PROFESSIONAL TAX", "EXCESS LEAVES", "TOTAL DEDUCTION", "NET SALARY",
                "ACCOUNT NO", "REMARKS", "COST CENTRE", "DEPT"
            ])}

            # Set column widths and merge cells for title (unchanged)
            worksheet.set_column(0, 28, 15)
            worksheet.merge_range('A1:AF1', 'Payroll Report', merge_format)
            worksheet.merge_range('A2:AF2', f'Report Date: {self.date_from} to {self.date_to}', merge_format)

            # Define headers
            headers = [
                "S.NO", "EMP. CODE", "NAME", "DESIGNATION", "CONTRACT TYPE",
                "EMPLOYEE CATEGORY", "NO. OF DAYS",
                f"SALARY AS ON {self.date_from - timedelta(days=1):%d-%m-%Y}",
                "INCREMENT/SALARY ADJUSTMENT", f"SALARY W.E.F. {self.date_from}",
                "BASIC PAY", "HR ALLOW", "CONV. ALLOW", "UTILITIES ALLOW",
                "MEDICAL ALLOW", "OTHER ALLOWANCES", "ARREARS", "OVERTIME/DRIVER ALLOW", "GROSS PAY",
                "INCOME TAX", "PROVIDENT FUND", "EOBI", "FOOD CHARGES", "ADVANCE",
                "Provident Fund Loan", "PROFESSIONAL TAX", "EXCESS LEAVES", "TOTAL DEDUCTION", "NET SALARY",
                "ACCOUNT NO", "REMARKS", "COST CENTRE", "DEPT"
            ]

            # Initialize models and departments (unchanged)
            payslip_model = self.env['hr.payslip']
            payslip_line_model = self.env['hr.payslip.line']
            departments = self.env['hr.department'].search([], order='master_department_id asc, name asc')

            # Set page layout (unchanged)
            worksheet.set_paper(9)
            worksheet.set_landscape()
            worksheet.set_margins(0.2, 0.2, 0.2, 0.2)
            worksheet.set_print_scale(100)
            worksheet.set_default_row(35)
            worksheet.fit_to_pages(1, 0)

            row = 3
            serial_no = 1
            row_list = []
            grand_totals = {
                'no_of_days': 0, 'salary_as_on': 0, 'increment': 0, 'salary_wef': 0,
                'basic_pay': 0, 'hr_allow': 0, 'conv_allow': 0, 'util_allow': 0,
                'med_allow': 0, 'arrears_others': 0, 'arrears': 0, 'overtime': 0, 'gross_pay': 0,
                'income_tax': 0, 'prov_fund': 0, 'eobi': 0, 'food_charges': 0,
                'advance': 0, 'pf_loan': 0, 'prof_tax': 0, 'excess_leaves': 0,
                'total_deduction': 0, 'net_salary': 0
            }

            # Iterate through departments
            for dept in departments:
                employees = self.env['hr.employee'].search([('department_id', '=', dept.id)], order='grade_id asc')
                if not employees:
                    continue

                # Initialize department totals
                dept_totals = {
                    'no_of_days': 0, 'salary_as_on': 0, 'increment': 0, 'salary_wef': 0,
                    'basic_pay': 0, 'hr_allow': 0, 'conv_allow': 0, 'util_allow': 0,
                    'med_allow': 0, 'arrears_others': 0, 'arrears': 0, 'overtime': 0, 'gross_pay': 0,
                    'income_tax': 0, 'prov_fund': 0, 'eobi': 0, 'food_charges': 0,
                    'advance': 0, 'pf_loan': 0, 'prof_tax': 0, 'excess_leaves': 0,
                    'total_deduction': 0, 'net_salary': 0
                }

                # Write department header and column headers
                worksheet.merge_range(row, 0, row, 3, f"Department: {dept.name}", dept_format)
                worksheet.write(row + 1, 0, headers[0], bold)
                worksheet.write(row + 1, 1, headers[1], bold)
                worksheet.write(row + 1, 2, headers[2], bold)
                worksheet.write(row + 1, 3, headers[3], bold)
                worksheet.write(row + 1, 4, headers[4], bold)
                worksheet.write(row + 1, 5, headers[5], bold)
                worksheet.write(row + 1, 6, headers[6], bold)
                worksheet.write(row + 1, 7, headers[7], bold)
                worksheet.write(row + 1, 8, headers[8], bold)
                worksheet.write(row + 1, 9, headers[9], bold)
                worksheet.merge_range(row + 1, 10, row + 1, 17, 'Pay and Allowance', merge_format)
                worksheet.write(row + 2, 10, headers[10], merge_format)
                worksheet.write(row + 2, 11, headers[11], merge_format)
                worksheet.write(row + 2, 12, headers[12], merge_format)
                worksheet.write(row + 2, 13, headers[13], merge_format)
                worksheet.write(row + 2, 14, headers[14], merge_format)
                worksheet.write(row + 2, 15, headers[15], merge_format)
                worksheet.write(row + 2, 16, headers[16], merge_format)
                worksheet.write(row + 2, 17, headers[17], merge_format)
                worksheet.write(row + 1, 18, headers[18], bold)
                worksheet.merge_range(row + 1, 19, row + 1, 26, 'Deduction', merge_format)
                worksheet.write(row + 2, 19, headers[19], merge_format)
                worksheet.write(row + 2, 20, headers[20], merge_format)
                worksheet.write(row + 2, 21, headers[21], merge_format)
                worksheet.write(row + 2, 22, headers[22], merge_format)
                worksheet.write(row + 2, 23, headers[23], merge_format)
                worksheet.write(row + 2, 24, headers[24], merge_format)
                worksheet.write(row + 2, 25, headers[25], merge_format)
                worksheet.write(row + 2, 26, headers[26], merge_format)
                worksheet.write(row + 1, 27, headers[27], bold)
                worksheet.write(row + 1, 28, headers[28], bold)
                worksheet.write(row + 1, 29, headers[29], bold)
                worksheet.write(row + 1, 30, headers[30], bold)
                worksheet.write(row + 1, 31, headers[31], bold)
                worksheet.write(row + 1, 32, headers[32], bold)

                row += 3

                # Collect employee data
                employee_data_list = []
                for emp in employees:
                    payslips = payslip_model.search([
                        ('employee_id', '=', emp.id),
                        ('date_from', '>=', self.date_from),
                        ('date_to', '<=', self.date_to)
                    ])

                    attendances = self.env['import.attendance'].search([
                        ('employee_id', '=', emp.id)
                    ])
                    line_amounts = {}
                    for payslip in payslips:
                        payslip_lines = payslip_line_model.search([('slip_id', '=', payslip.id)])
                        for line in payslip_lines:
                            if line.name:
                                line_amounts[line.name] = line_amounts.get(line.name, 0.0) + line.total

                    # Calculate total deductions
                    total_deductions = (
                        line_amounts.get('Income Tax', 0.0) +
                        line_amounts.get('Provident Fund', 0.0) +
                        line_amounts.get('EOBI', 0.0) +
                        line_amounts.get('Food Charges', 0.0) +
                        line_amounts.get('Advance', 0.0) +
                        line_amounts.get('Provident Fund Loan', 0.0) +
                        line_amounts.get('Professional Tax', 0.0) +
                        line_amounts.get('Excess Leaves', 0.0)
                    )

                    # Get net salary
                    payslip_emp = payslip_model.search([('employee_id', '=', emp.id), ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)], limit=1)
                    net_salary = payslip_emp.net_wage if payslip_emp else 0.0

                    # Store employee data
                    employee_data = {
                        'sr_no': serial_no,
                        'sort_id': emp.x_studio_sort_id or '',
                        'employee_code': emp.employee_id or '',
                        'name': emp.name or '',
                        'designation': emp.job_id.name or '',
                        'contract_type': emp.contract_type.name or '',
                        'employee_category': emp.employee_category.name or '',
                        'no_of_days': attendances.present_days if attendances else 0,
                        'salary_as_on': emp.contract_id.wage,
                        'increment': emp.contract_id.increment,
                        'salary_wef': emp.contract_id.wage + emp.contract_id.increment,
                        'basic_pay': round(line_amounts.get('Basic Salary', 0.0), 2),
                        'hr_allow': round(line_amounts.get('House Rent Allowance', 0.0), 2),
                        'conv_allow': round(line_amounts.get('Conveyance Allowance', 0.0), 2),
                        'util_allow': round(line_amounts.get('Utilities Allowance', 0.0), 2),
                        'med_allow': round(line_amounts.get('Medical Allowance', 0.0), 2),
                        'arrears_others': round(line_amounts.get('Other Allowance', 0.0), 2),
                        'arrears': round(line_amounts.get('Arrears', 0.0), 2),
                        'overtime': round(line_amounts.get('Overtime', 0.0), 2),
                        'gross_pay': round(line_amounts.get('Gross', 0.0), 2),
                        'income_tax': round(line_amounts.get('Income Tax', 0.0), 2),
                        'prov_fund': round(line_amounts.get('Provident Fund', 0.0), 2),
                        'eobi': round(line_amounts.get('EOBI', 0.0), 2),
                        'food_charges': round(line_amounts.get('Food Charges', 0.0), 2),
                        'advance': round(line_amounts.get('Advance', 0.0), 2),
                        'pf_loan': round(line_amounts.get('Provident Fund Loan', 0.0), 2),
                        'prof_tax': round(line_amounts.get('Professional Tax', 0.0), 2),
                        'excess_leaves': round(line_amounts.get('Excess Leaves', 0.0), 2),
                        'total_deduction': round(total_deductions, 2),
                        'net_salary': round(net_salary, 2),
                        'account_no': emp.bank_account_id.acc_number if emp.bank_account_id and emp.bank_account_id.acc_number else '',
                        'remarks': '',
                        'cost_centre': f"[{emp.contract_id.analytic_account_id.code}] {emp.contract_id.analytic_account_id.name}" if emp.contract_id and emp.contract_id.analytic_account_id else '',
                        'dept': emp.department_id.name or ''
                    }
                    employee_data_list.append(employee_data)
                    serial_no += 1

                # Sort employee data by sr_no
                sorted_employee_data = self.sort_employee_data(employee_data_list, sort_by='sort_id')

                # Write sorted employee data to worksheet
                count = 0
                for emp_data in sorted_employee_data:
                    count += 1
                    worksheet.write(row, 0, count, normal)
                    worksheet.write(row, 1, emp_data['employee_code'], normal)
                    worksheet.write(row, 2, emp_data['name'], normal)
                    worksheet.write(row, 3, emp_data['designation'], normal)
                    worksheet.write(row, 4, emp_data['contract_type'], normal)
                    worksheet.write(row, 5, emp_data['employee_category'], normal)
                    worksheet.write(row, 6, emp_data['no_of_days'], normal)
                    worksheet.write(row, 7, emp_data['salary_as_on'], number_format)
                    worksheet.write(row, 8, emp_data['increment'], number_format)
                    worksheet.write(row, 9, emp_data['salary_wef'], number_format)
                    worksheet.write(row, 10, emp_data['basic_pay'], number_format)
                    worksheet.write(row, 11, emp_data['hr_allow'], number_format)
                    worksheet.write(row, 12, emp_data['conv_allow'], number_format)
                    worksheet.write(row, 13, emp_data['util_allow'], number_format)
                    worksheet.write(row, 14, emp_data['med_allow'], number_format)
                    worksheet.write(row, 15, emp_data['arrears_others'], number_format)
                    worksheet.write(row, 16, emp_data['arrears'], number_format)
                    worksheet.write(row, 17, emp_data['overtime'], number_format)
                    worksheet.write(row, 18, emp_data['gross_pay'], number_format)
                    worksheet.write(row, 19, emp_data['income_tax'], number_format)
                    worksheet.write(row, 20, emp_data['prov_fund'], number_format)
                    worksheet.write(row, 21, emp_data['eobi'], number_format)
                    worksheet.write(row, 22, emp_data['food_charges'], number_format)
                    worksheet.write(row, 23, emp_data['advance'], number_format)
                    worksheet.write(row, 24, emp_data['pf_loan'], number_format)
                    worksheet.write(row, 25, emp_data['prof_tax'], number_format)
                    worksheet.write(row, 26, emp_data['excess_leaves'], number_format)
                    worksheet.write(row, 27, emp_data['total_deduction'], number_format)
                    worksheet.write(row, 28, emp_data['net_salary'], number_format)
                    worksheet.write(row, 29, emp_data['account_no'], normal)
                    worksheet.write(row, 30, emp_data['remarks'], normal)
                    worksheet.write(row, 31, emp_data['cost_centre'], normal)
                    worksheet.write(row, 32, emp_data['dept'], normal)

                    # Update department totals
                    dept_totals['no_of_days'] += emp_data['no_of_days']
                    dept_totals['salary_as_on'] += emp_data['salary_as_on']
                    dept_totals['increment'] += emp_data['increment']
                    dept_totals['salary_wef'] += emp_data['salary_wef']
                    dept_totals['basic_pay'] += emp_data['basic_pay']
                    dept_totals['hr_allow'] += emp_data['hr_allow']
                    dept_totals['conv_allow'] += emp_data['conv_allow']
                    dept_totals['util_allow'] += emp_data['util_allow']
                    dept_totals['med_allow'] += emp_data['med_allow']
                    dept_totals['arrears_others'] += emp_data['arrears_others']
                    dept_totals['arrears'] += emp_data['arrears']
                    dept_totals['overtime'] += emp_data['overtime']
                    dept_totals['gross_pay'] += emp_data['gross_pay']
                    dept_totals['income_tax'] += emp_data['income_tax']
                    dept_totals['prov_fund'] += emp_data['prov_fund']
                    dept_totals['eobi'] += emp_data['eobi']
                    dept_totals['food_charges'] += emp_data['food_charges']
                    dept_totals['advance'] += emp_data['advance']
                    dept_totals['pf_loan'] += emp_data['pf_loan']
                    dept_totals['prof_tax'] += emp_data['prof_tax']
                    dept_totals['excess_leaves'] += emp_data['excess_leaves']
                    dept_totals['total_deduction'] += emp_data['total_deduction']
                    dept_totals['net_salary'] += emp_data['net_salary']

                    row += 1

                # Update grand totals
                for key in grand_totals:
                    grand_totals[key] += dept_totals[key]

                # Write department subtotal
                worksheet.merge_range(row, 0, row, 3, f"Subtotal for {dept.name}", subtotal_format)
                worksheet.write(row, 6, dept_totals['no_of_days'], number_format)
                worksheet.write(row, 7, round(dept_totals['salary_as_on'], 2), number_format)
                worksheet.write(row, 8, round(dept_totals['increment'], 2), number_format)
                worksheet.write(row, 9, round(dept_totals['salary_wef'], 2), number_format)
                worksheet.write(row, 10, round(dept_totals['basic_pay'], 2), number_format)
                worksheet.write(row, 11, round(dept_totals['hr_allow'], 2), number_format)
                worksheet.write(row, 12, round(dept_totals['conv_allow'], 2), number_format)
                worksheet.write(row, 13, round(dept_totals['util_allow'], 2), number_format)
                worksheet.write(row, 14, round(dept_totals['med_allow'], 2), number_format)
                worksheet.write(row, 15, round(dept_totals['arrears_others'], 2), number_format)
                worksheet.write(row, 16, round(dept_totals['arrears'], 2), number_format)
                worksheet.write(row, 17, round(dept_totals['overtime'], 2), number_format)
                worksheet.write(row, 18, round(dept_totals['gross_pay'], 2), number_format)
                worksheet.write(row, 19, round(dept_totals['income_tax'], 2), number_format)
                worksheet.write(row, 20, round(dept_totals['prov_fund'], 2), number_format)
                worksheet.write(row, 21, round(dept_totals['eobi'], 2), number_format)
                worksheet.write(row, 22, round(dept_totals['food_charges'], 2), number_format)
                worksheet.write(row, 23, round(dept_totals['advance'], 2), number_format)
                worksheet.write(row, 24, round(dept_totals['pf_loan'], 2), number_format)
                worksheet.write(row, 25, round(dept_totals['prof_tax'], 2), number_format)
                worksheet.write(row, 26, round(dept_totals['excess_leaves'], 2), number_format)
                worksheet.write(row, 27, round(dept_totals['total_deduction'], 2), number_format)
                worksheet.write(row, 28, round(dept_totals['net_salary'], 2), number_format)

                row += 1
                worksheet.write(row, 0, '')
                row += 1
                row_list.append(row)

            # Write grand total
            worksheet.merge_range(row, 0, row, 3, "Grand Total", grand_total_format)
            worksheet.write(row, 6, grand_totals['no_of_days'], number_format)
            worksheet.write(row, 7, round(grand_totals['salary_as_on'], 2), number_format)
            worksheet.write(row, 8, round(grand_totals['increment'], 2), number_format)
            worksheet.write(row, 9, round(grand_totals['salary_wef'], 2), number_format)
            worksheet.write(row, 10, round(grand_totals['basic_pay'], 2), number_format)
            worksheet.write(row, 11, round(grand_totals['hr_allow'], 2), number_format)
            worksheet.write(row, 12, round(grand_totals['conv_allow'], 2), number_format)
            worksheet.write(row, 13, round(grand_totals['util_allow'], 2), number_format)
            worksheet.write(row, 14, round(grand_totals['med_allow'], 2), number_format)
            worksheet.write(row, 15, round(grand_totals['arrears_others'], 2), number_format)
            worksheet.write(row, 16, round(grand_totals['arrears'], 2), number_format)
            worksheet.write(row, 17, round(grand_totals['overtime'], 2), number_format)
            worksheet.write(row, 18, round(grand_totals['gross_pay'], 2), number_format)
            worksheet.write(row, 19, round(grand_totals['income_tax'], 2), number_format)
            worksheet.write(row, 20, round(grand_totals['prov_fund'], 2), number_format)
            worksheet.write(row, 21, round(grand_totals['eobi'], 2), number_format)
            worksheet.write(row, 22, round(grand_totals['food_charges'], 2), number_format)
            worksheet.write(row, 23, round(grand_totals['advance'], 2), number_format)
            worksheet.write(row, 24, round(grand_totals['pf_loan'], 2), number_format)
            worksheet.write(row, 25, round(grand_totals['prof_tax'], 2), number_format)
            worksheet.write(row, 26, round(grand_totals['excess_leaves'], 2), number_format)
            worksheet.write(row, 27, round(grand_totals['total_deduction'], 2), number_format)
            worksheet.write(row, 28, round(grand_totals['net_salary'], 2), number_format)

            row += 1

            # Set custom column widths
            inch_to_width = 7.5
            inches_list = [0.6, 1.1, 4.2, 6, 2, 2.2, 1.5, 2.5, 3.3, 2.8, 1.5, 1.5, 2, 2, 1.8, 1.5, 1.5, 2.6, 1.6, 1.5, 2, 1.5, 1.8, 1.6, 1, 2, 2, 2, 1.5, 3.3, 2, 5.5, 4.5]
            added_widths = [inch_to_width * inches for inches in inches_list]

            for col in range(len(column_widths)):
                worksheet.set_column(col, col, column_widths[col] + added_widths[col])

            worksheet.set_h_pagebreaks(row_list)
            workbook.close()
            output.seek(0)

            wizard = self.env['payroll.report'].create({'excel_file': base64.b64encode(output.getvalue())})
            output.close()

            filename = f'Salary_Report_Grouped_By_Department.xls'

            return {
                'type': 'ir.actions.act_url',
                'name': _("Salary Report"),
                'url': f"/web/content/{self._name}/{wizard.id}/excel_file/{filename}?download=true",
                'target': 'self'
            }