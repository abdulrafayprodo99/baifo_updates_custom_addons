from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
from io import BytesIO

class AllowanceReportWizard(models.TransientModel):
    _name = 'allowance.report.wizard'
    _description = 'Allowance Report Wizard'

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
    ], string='Month', required=True)

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, 2050)],
        string='Year',
        required=True
    )

    allowance_type = fields.Selection([
        ('eobi', 'EOBI'),
        ('social_security', 'Social Security'),
        ('food_charges', 'Food Charges'),
        ('provident_fund', 'Provident Fund')
    ], string='Allowance Type', required=True)
    
    report_type = fields.Selection(
        [('pdf', 'PDF'), ('excel', 'Excel')],
        string='Report Format',
        default='pdf',
    )

    def generate_report(self):
        data = {
            'month': self.month,
            'year': self.year,
            'allowance_type': self.allowance_type,
        }

        report_data = self.get_report_data(data)


        # raise UserError(str(report_data))

        if self.report_type == 'pdf':
            return self.env.ref('consolidated_allowance_deduction_reports.action_allowance_report').report_action(self, data={'report_data': report_data})
        else:
            return self.generate_excel(report_data)



    def get_report_data(self, data):
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

        # raise UserError(str(allowances.read()))
        departments_data = {}
        for allowance in allowances:
            parent_dept = allowance.employee_id.department_id.parent_id
            sub_dept = allowance.employee_id.department_id
            
            parent_dept_key = parent_dept.id
            sub_dept_key = sub_dept.id
            
            if parent_dept_key not in departments_data:
                departments_data[parent_dept_key] = {
                    'parent_department': parent_dept.name,
                    'sub_departments': {}
                }
            
            if sub_dept_key not in departments_data[parent_dept_key]['sub_departments']:
                departments_data[parent_dept_key]['sub_departments'][sub_dept_key] = {
                    'name': sub_dept.name,
                    'employee_count': 0,
                    'employee_contribution': 0,
                    'employer_contribution': 0,
                    'total': 0
                }
            
            sub_dept_data = departments_data[parent_dept_key]['sub_departments'][sub_dept_key]
            sub_dept_data['employee_count'] += 1
            sub_dept_data['employee_contribution'] += getattr(allowance, employee_field, 0)
            sub_dept_data['employer_contribution'] += getattr(allowance, employer_field, 0)
            sub_dept_data['total'] += getattr(allowance, employee_field, 0) + getattr(allowance, employer_field, 0)

        report_data = {
            'month': data['month'],
            'year': data['year'],
            'allowance_type': data['allowance_type'],
            'departments': list(departments_data.values()),
            'grand_totals': {
                'employee_contribution': sum(
                    sub_dept.get('employee_contribution', 0)
                    for dept in departments_data.values()
                    for sub_dept in dept['sub_departments'].values()
                ),
                'employer_contribution': sum(
                    sub_dept.get('employer_contribution', 0)
                    for dept in departments_data.values()
                    for sub_dept in dept['sub_departments'].values()
                ),
                'total': sum(
                    sub_dept.get('total', 0)
                    for dept in departments_data.values()
                    for sub_dept in dept['sub_departments'].values()
                )
            }
        }
        return report_data



    # def generate_excel(self, report_data):
    #     # Create a BytesIO buffer
    #     buffer = BytesIO()

    #     # Create an Excel file
    #     workbook = xlsxwriter.Workbook(buffer)
    #     worksheet = workbook.add_worksheet("Allowance Report")

    #     # Define styles
    #     title_format = workbook.add_format({
    #         'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_color': '#000000'
    #     })
    #     header_format = workbook.add_format({
    #         'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D9E1F2'
    #     })
    #     parent_department_format = workbook.add_format({
    #         'bold': True, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': '#CFE2F3', 'font_color': '#000000'
    #     })
    #     subheader_format = workbook.add_format({
    #         'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': '#F4F4F4'
    #     })
    #     number_format = workbook.add_format({
    #         'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'
    #     })
    #     total_format = workbook.add_format({
    #         'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#D9E1F2'
    #     })
    #     grand_total_format = workbook.add_format({
    #         'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#B7DEE8'
    #     })
    #     grand_total_label_format = workbook.add_format({
    #         'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#B7DEE8'
    #     })

    #     # Merge and write the title
    #     worksheet.merge_range('A1:E1', 'BIAFO INDUSTRIES LIMITED', title_format)
    #     worksheet.merge_range('A2:E2', 'Allowance Report', title_format)
    #     worksheet.merge_range('A3:E3', f"Allowance Type: {report_data['allowance_type'].replace('_', ' ').capitalize()}", title_format)
    #     worksheet.merge_range('A4:E4', f"For {report_data['month']} {report_data['year']}", title_format)

    #     # Write headers
    #     worksheet.write('A6', 'S.No', header_format)
    #     worksheet.write('B6', 'Department', header_format)
    #     worksheet.write('C6', 'Employee Contribution', header_format)
    #     worksheet.write('D6', 'Employer Contribution', header_format)
    #     worksheet.write('E6', 'Total', header_format)

    #     # Set column widths
    #     worksheet.set_column('A:A', 5)
    #     worksheet.set_column('B:B', 40)
    #     worksheet.set_column('C:E', 18)

    #     # Write data
    #     row = 6
    #     s_no = 1

    #     for dept_index, department in enumerate(report_data['departments'], start=1):
    #         # Write parent department row with special styling
    #         worksheet.merge_range(row, 0, row, 4, f"{dept_index} - {department['parent_department']}", parent_department_format)
    #         row += 1

    #         # Write sub-department rows
    #         for sub_index, sub_dept in enumerate(department['sub_departments'].values(), start=1):
    #             worksheet.write(row, 0, sub_index, subheader_format)
    #             worksheet.write(row, 1, sub_dept['name'], subheader_format)
    #             worksheet.write(row, 2, sub_dept['employee_contribution'], number_format)
    #             worksheet.write(row, 3, sub_dept['employer_contribution'], number_format)
    #             worksheet.write(row, 4, sub_dept['total'], number_format)
    #             row += 1

    #     # Write grand totals
    #     worksheet.merge_range(row, 0, row, 1, 'Grand Total', grand_total_label_format)
    #     worksheet.write(row, 2, report_data['grand_totals']['employee_contribution'], grand_total_format)
    #     worksheet.write(row, 3, report_data['grand_totals']['employer_contribution'], grand_total_format)
    #     worksheet.write(row, 4, report_data['grand_totals']['total'], grand_total_format)

    #     # Close the workbook
    #     workbook.close()

    #     # Save the buffer content as a binary field
    #     buffer.seek(0)
    #     excel_data = buffer.getvalue()
    #     buffer.close()

    #     # Return Excel file as an attachment
    #     attachment = self.env['ir.attachment'].create({
    #         'name': 'Allowance_Report.xlsx',
    #         'type': 'binary',
    #         'datas': base64.b64encode(excel_data),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     })
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'self',
    #     }



    def generate_excel(self, report_data):
        from io import BytesIO
        import base64
        import xlsxwriter

        # Create a BytesIO buffer
        buffer = BytesIO()

        # Create an Excel file
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet("Allowance Report")

        # Define styles
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_color': '#000000'
        })
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D9E1F2'
        })
        parent_department_format = workbook.add_format({
            'bold': True, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': '#CFE2F3', 'font_color': '#000000'
        })
        subheader_format = workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': '#F4F4F4'
        })
        number_format = workbook.add_format({
            'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'
        })
        total_format = workbook.add_format({
            'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#D9E1F2'
        })
        grand_total_format = workbook.add_format({
            'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#B7DEE8'
        })
        grand_total_label_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#B7DEE8'
        })

        # Merge and write the title
        worksheet.merge_range('A1:E1', 'BIAFO INDUSTRIES LIMITED', title_format)
        worksheet.merge_range('A2:E2', 'Allowance Report', title_format)
        worksheet.merge_range('A3:E3', f"Allowance Type: {report_data['allowance_type'].replace('_', ' ').capitalize()}", title_format)
        worksheet.merge_range('A4:E4', f"For {report_data['month']} {report_data['year']}", title_format)

        # Write headers
        worksheet.write('A6', 'S.No', header_format)
        worksheet.write('B6', 'Department', header_format)
        worksheet.write('C6', 'Employee Contribution', header_format)
        worksheet.write('D6', 'Employer Contribution', header_format)
        worksheet.write('E6', 'Total', header_format)

        # Set column widths
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:E', 18)

        # Write data
        row = 6
        s_no = 1

        for dept_index, department in enumerate(report_data['departments'], start=1):
            # Check if the parent department has any sub-department with a total > 0
            valid_sub_depts = [
                sub_dept for sub_dept in department['sub_departments'].values()
                if sub_dept['total'] > 0
            ]
            if not valid_sub_depts:
                continue  # Skip this parent department if no valid sub-departments

            # Write parent department row with special styling
            worksheet.merge_range(row, 0, row, 4, f"{dept_index} - {department['parent_department']}", parent_department_format)
            row += 1

            # Write sub-department rows
            for sub_index, sub_dept in enumerate(valid_sub_depts, start=1):
                worksheet.write(row, 0, sub_index, subheader_format)
                worksheet.write(row, 1, sub_dept['name'], subheader_format)
                worksheet.write(row, 2, sub_dept['employee_contribution'], number_format)
                worksheet.write(row, 3, sub_dept['employer_contribution'], number_format)
                worksheet.write(row, 4, sub_dept['total'], number_format)
                row += 1

        # Write grand totals
        worksheet.merge_range(row, 0, row, 1, 'Grand Total', grand_total_label_format)
        worksheet.write(row, 2, report_data['grand_totals']['employee_contribution'], grand_total_format)
        worksheet.write(row, 3, report_data['grand_totals']['employer_contribution'], grand_total_format)
        worksheet.write(row, 4, report_data['grand_totals']['total'], grand_total_format)

        # Close the workbook
        workbook.close()

        # Save the buffer content as a binary field
        buffer.seek(0)
        excel_data = buffer.getvalue()
        buffer.close()

        # Return Excel file as an attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Allowance_Report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(excel_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
