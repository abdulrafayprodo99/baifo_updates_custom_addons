from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
from io import BytesIO
import re

class AllowancesDeductionReport(models.TransientModel):
    _name = 'allowance.details.wizard'
    _description = 'Allowances Details Wizard'

    month = fields.Selection([
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], string='Month')

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, 2050)],
        string='Year',
    )
    allowance_type = fields.Selection([
        ('eobi', 'EOBI'),
        ('social_security', 'Social Security'),
        ('food_charges', 'Food Charges'),
        ('provident_fund', 'Provident Fund')
    ], string="Allowance Type")

    report_type = fields.Selection(
        [('pdf', 'PDF'), ('excel', 'Excel')],
        string='Report Format',
        default='pdf',  # default to PDF
    )

    # def generate_report(self):
    #     data = {
    #         'year': self.year,
    #         'month': self.month,
    #         'allowance_type': self.allowance_type,
    #     }

    #     report_data = self.get_report_data(data)  # Get the report data for both PDF and Excel

    #     # raise UserError(str(report_data))

    #     if self.report_type == 'pdf':
    #         return self.env.ref('consolidated_allowance_deduction_reports.action_allowance_details').report_action(self, data={'report_data': report_data})
    #     else:
    #         return self.generate_excel(report_data)
    def generate_report(self):
        data = {
            'year': self.year,
            'month': self.month,
            'allowance_type': self.allowance_type,
        }

        # Get the report data
        report_data = self.get_report_data(data)
        
        # Sort the report data to ensure 'Head Office' comes before 'Factory' and sub-departments are sorted
        sorted_report_data = self.sort_report_data(report_data)

        if self.report_type == 'pdf':
            return self.env.ref('consolidated_allowance_deduction_reports.action_allowance_details').report_action(self, data={'report_data': sorted_report_data})
        else:
            return self.generate_excel(sorted_report_data)

    def sort_report_data(self, report_data):
        """
        Sorts the report_data to ensure 'Head Office' comes before 'Factory' and
        sub-departments are sorted sequentially by their numeric prefix.
        
        Args:
            report_data (dict): The report data dictionary containing grouped_data and other fields.
        
        Returns:
            dict: A new report_data dictionary with sorted parent and sub-departments.
        """


        # Create a copy of report_data to avoid modifying the original
        sorted_report_data = report_data.copy()
        
        # Helper function to extract numeric prefix from department names
        def get_numeric_prefix(name):
            match = re.match(r'(\d+)-', name)
            return int(match.group(1)) if match else float('inf')

        # Sort parent departments: '1-Head Office' first, then '2-Factory'
        sorted_grouped_data = {}
        for parent_dept in sorted(report_data['grouped_data'].keys(), key=lambda x: x != '1-Head Office'):
            # Sort sub-departments by numeric prefix
            sorted_sub_depts = {}
            for sub_dept in sorted(report_data['grouped_data'][parent_dept].keys(), key=get_numeric_prefix):
                sorted_sub_depts[sub_dept] = report_data['grouped_data'][parent_dept][sub_dept]
            sorted_grouped_data[parent_dept] = sorted_sub_depts
        
        # Update the grouped_data field with the sorted structure
        sorted_report_data['grouped_data'] = sorted_grouped_data
        
        return sorted_report_data

    def get_report_data(self, data):
        # Map allowance types to fields
        allowance_field_map = {
            'eobi': ('eobi_contribution', 'eobi_employer_contribution'),
            'social_security': ('ss_employee_contribution', 'ss_employer_contribution'),
            'food_charges': ('food_employee_contribution', 'food_employer_contribution'),
            'provident_fund': ('pf_employee_contribution', 'pf_employer_contribution'),
        }

        allowance_fields = allowance_field_map.get(data['allowance_type'])
        if not allowance_fields:
            raise UserError(_('Invalid Allowance Type'))

        employee_field, employer_field = allowance_fields

        # Extract year and month
        year = data['year']
        month = data['month']

        # List of month names in order
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        # Ensure the selected month is valid
        if month not in month_names:
            raise UserError(_('Invalid month selected'))

        # Build domain based on year and month


        domain = [
            ('year', '=', str(year)),
            ('month', '=', month.lower()),
        ]

        allowances = self.env['allowances.deduction'].search(domain)


        # Group data by Parent Department, then Sub Department, then Employee
        grouped_data = {}

        for allowance in allowances:
            employee = allowance.employee_id
            parent_department = employee.department_id.parent_id
            sub_department = employee.department_id

            if not parent_department:
                continue

            if parent_department.name not in grouped_data:
                grouped_data[parent_department.name] = {}

            if sub_department.name not in grouped_data[parent_department.name]:
                grouped_data[parent_department.name][sub_department.name] = []

            # Employee data
            employee_data = {
                'emp_code': employee.employee_id,
                'emp_name': employee.name,
                'emp_sr_no': employee.x_studio_sort_id,
                'designation': employee.job_id.name,
                'employee_contribution': getattr(allowance, employee_field, 0),
                'employer_contribution': getattr(allowance, employer_field, 0),
                'total': getattr(allowance, employee_field, 0) + getattr(allowance, employer_field, 0),
            }
            # employee_data = sorted(employee_data, key=lambda x: x['emp_sr_no'])

        
            # Append the employee data
            grouped_data[parent_department.name][sub_department.name].append(employee_data)

            # Sort the list by 'emp_sr_no' after appending
            grouped_data[parent_department.name][sub_department.name].sort(key=lambda x: x['emp_sr_no'])





        # Include dates and allowance type in the return structure
        report_data = {
            'year': data['year'],
            'month': data['month'],
            'allowance_type': data['allowance_type'],
            'grouped_data': grouped_data,
        }

        # Calculate Grand Totals
        grand_totals = {
            'employee_contribution': sum(emp['employee_contribution'] for dept in grouped_data.values() for sub_dept in dept.values() for emp in sub_dept),
            'employer_contribution': sum(emp['employer_contribution'] for dept in grouped_data.values() for sub_dept in dept.values() for emp in sub_dept),
            'total': sum(emp['total'] for dept in grouped_data.values() for sub_dept in dept.values() for emp in sub_dept),
        }

        report_data['grand_totals'] = grand_totals

        return report_data
        raise UserError(str(report_data))
    



    # def generate_excel(self, report_data):
    #     # Create an in-memory Excel file
    #     output = BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet('Food Charges Report')

    #     # Define formats
    #     title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
    #     header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D3D3D3'})
    #     sub_header_format = workbook.add_format({'bold': True, 'align': 'left'})
    #     text_format = workbook.add_format({'border': 1, 'align': 'left'})
    #     number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})

    #     # Dynamic title based on allowance type
    #     allowance_type = report_data.get('allowance_type', 'Allowance Report').upper()

    #     # Titl2
    #     worksheet.merge_range('A1:G1', 'BIAFO INDUSTRIES LIMITED', title_format)
    #     worksheet.merge_range('A2:G2', allowance_type, title_format)
    #     worksheet.merge_range('A3:G3', f"Employee / Management Contribution", title_format)
    #     worksheet.merge_range('A4:G4', f"For {report_data['month']} {report_data['year']}", title_format)

    #     # Column Headers
    #     headers = ['S.No', 'EMP.CODE', 'NAME', 'DESIGNATION', 'Employee Contribution', 'Employer Contribution', 'Total']
    #     for col_num, header in enumerate(headers):
    #         worksheet.write(4, col_num, header, header_format)

    #     # Populate data
    #     row = 6
    #     sno = 1

    #     for parent_dept, sub_depts in report_data['grouped_data'].items():
    #         worksheet.write(row, 0, '', sub_header_format)
    #         worksheet.merge_range(row, 0, row, 6, parent_dept, sub_header_format)
    #         row += 1

    #         for sub_dept, employees in sub_depts.items():
    #             worksheet.write(row, 0, '', sub_header_format)
    #             worksheet.merge_range(row, 0, row, 6, f"  {sub_dept}", sub_header_format)
    #             row += 1

    #             for emp in employees:
    #                 worksheet.write(row, 0, sno, text_format)
    #                 worksheet.write(row, 1, emp['emp_code'], text_format)
    #                 worksheet.write(row, 2, emp['emp_name'], text_format)
    #                 worksheet.write(row, 3, emp['designation'], text_format)
    #                 worksheet.write(row, 4, emp['employee_contribution'], number_format)
    #                 worksheet.write(row, 5, emp['employer_contribution'], number_format)
    #                 worksheet.write(row, 6, emp['total'], number_format)
    #                 row += 1
    #                 sno += 1

    #             # Subtotal row
    #             subtotal = {
    #                 'employee_contribution': sum(e['employee_contribution'] for e in employees),
    #                 'employer_contribution': sum(e['employer_contribution'] for e in employees),
    #                 'total': sum(e['total'] for e in employees),
    #             }
    #             worksheet.write(row, 3, 'SUB TOTAL', header_format)
    #             worksheet.write(row, 4, subtotal['employee_contribution'], number_format)
    #             worksheet.write(row, 5, subtotal['employer_contribution'], number_format)
    #             worksheet.write(row, 6, subtotal['total'], number_format)
    #             row += 1

    #     # Grand total row
    #     worksheet.write(row, 3, 'GRAND TOTAL', header_format)
    #     worksheet.write(row, 4, report_data['grand_totals']['employee_contribution'], number_format)
    #     worksheet.write(row, 5, report_data['grand_totals']['employer_contribution'], number_format)
    #     worksheet.write(row, 6, report_data['grand_totals']['total'], number_format)

    #     # Adjust column widths
    #     worksheet.set_column('A:A', 5)
    #     worksheet.set_column('B:B', 10)
    #     worksheet.set_column('C:C', 30)
    #     worksheet.set_column('D:D', 30)
    #     worksheet.set_column('E:G', 20)

    #     workbook.close()
    #     output.seek(0)

    #     # Encode and return the file
    #     excel_data = base64.b64encode(output.read())
    #     output.close()

    #     attachment = self.env['ir.attachment'].create({
    #         'name': f"{allowance_type}_Report_{report_data['month']}_{report_data['year']}.xlsx",
    #         'type': 'binary',
    #         'datas': excel_data,
    #         'res_model': self._name,
    #         'res_id': self.id,
    #     })
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'new',
    # }



    def generate_excel(self, report_data):
        # Create an in-memory Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Food Charges Report')

        # Define formats
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D3D3D3'})
        sub_header_format = workbook.add_format({'bold': True, 'align': 'left'})
        text_format = workbook.add_format({'border': 1, 'align': 'left'})
        number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})

        # Dynamic title based on allowance type
        allowance_type = report_data.get('allowance_type', 'Allowance Report').upper()

        # Title
        worksheet.merge_range('A1:G1', 'BIAFO INDUSTRIES LIMITED', title_format)
        worksheet.merge_range('A2:G2', f"{report_data['allowance_type'].replace('_', ' ').upper()}", title_format)
        worksheet.merge_range('A3:G3', f"Employee / Management Contribution", title_format)
        worksheet.merge_range('A4:G4', f"For {report_data['month']} {report_data['year']}", title_format)

        # Column Headers
        headers = ['S.No', 'EMP.CODE', 'NAME', 'DESIGNATION', 'Employee Contribution', 'Employer Contribution', 'Total']
        for col_num, header in enumerate(headers):
            worksheet.write(4, col_num, header, header_format)

        # Populate data
        row = 6
        sno = 1

        # Filter grouped data
        filtered_grouped_data = {
            parent: {
                sub: emp_list
                for sub, emp_list in sub_depts.items()
                if sum(emp['total'] for emp in emp_list) > 0
            }
            for parent, sub_depts in report_data['grouped_data'].items()
            if any(sum(emp['total'] for emp in emp_list) > 0 for emp_list in sub_depts.values())
        }

        for parent_dept, sub_depts in filtered_grouped_data.items():
            worksheet.write(row, 0, '', sub_header_format)
            worksheet.merge_range(row, 0, row, 6, parent_dept, sub_header_format)
            row += 1

            for sub_dept, employees in sub_depts.items():
                worksheet.write(row, 0, '', sub_header_format)
                worksheet.merge_range(row, 0, row, 6, f"  {sub_dept}", sub_header_format)
                row += 1

                for emp in employees:
                    if emp['total'] > 0:
                        worksheet.write(row, 0, sno, text_format)
                        worksheet.write(row, 1, emp['emp_code'], text_format)
                        worksheet.write(row, 2, emp['emp_name'], text_format)
                        worksheet.write(row, 3, emp['designation'], text_format)
                        worksheet.write(row, 4, emp['employee_contribution'], number_format)
                        worksheet.write(row, 5, emp['employer_contribution'], number_format)
                        worksheet.write(row, 6, emp['total'], number_format)
                        row += 1
                        sno += 1

                # Subtotal row
                subtotal = {
                    'employee_contribution': sum(e['employee_contribution'] for e in employees),
                    'employer_contribution': sum(e['employer_contribution'] for e in employees),
                    'total': sum(e['total'] for e in employees),
                }
                worksheet.write(row, 3, 'SUB TOTAL', header_format)
                worksheet.write(row, 4, subtotal['employee_contribution'], number_format)
                worksheet.write(row, 5, subtotal['employer_contribution'], number_format)
                worksheet.write(row, 6, subtotal['total'], number_format)
                row += 1

        # Grand total row
        worksheet.write(row, 3, 'GRAND TOTAL', header_format)
        worksheet.write(row, 4, report_data['grand_totals']['employee_contribution'], number_format)
        worksheet.write(row, 5, report_data['grand_totals']['employer_contribution'], number_format)
        worksheet.write(row, 6, report_data['grand_totals']['total'], number_format)

        # Adjust column widths
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:G', 20)

        workbook.close()
        output.seek(0)

        # Encode and return the file
        excel_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': f"{allowance_type}_Report_{report_data['month']}_{report_data['year']}.xlsx",
            'type': 'binary',
            'datas': excel_data,
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
