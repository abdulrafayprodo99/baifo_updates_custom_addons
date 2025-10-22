from odoo import models, fields, api, _
from odoo.exceptions import UserError
import calendar
from datetime import timedelta


class ImportAttendance(models.Model):
    _name = "import.attendance"
    _rec_name = 'emp_id'

    emp_id = fields.Char(string='Employee ID')
    employee_id = fields.Many2one(string="Employee Name", comodel_name='hr.employee')
    job_id = fields.Many2one('hr.job', string='Designation')
    year = fields.Selection(
        selection=[(str(year), str(year)) for year in range(2000, 2031)],       string='Year',
    )
    month = fields.Selection(
        selection=[
            ('january', 'January'),
            ('february', 'February'),
            ('march', 'March'),
            ('april', 'April'),
            ('may', 'May'),
            ('june', 'June'),
            ('july', 'July'),
            ('august', 'August'),
            ('september', 'September'),
            ('october', 'October'),
            ('november', 'November'),
            ('december', 'December'),
        ],
        string='Month',
    )

    total_days = fields.Integer(string='Total Days', compute='_compute_total_days', store=True)
    present_days = fields.Integer(string='Present Days')

    def _create_attendance_records(self):
        for rec in self:
            if rec.employee_id and rec.present_days > 0 and rec.year and rec.month:
                attendance_model = self.env['hr.attendance']
                year = int(rec.year)
                month = list(dict(self._fields['month'].selection).keys()).index(rec.month) + 1
                present_days_count = 0

                for day in range(1, calendar.monthrange(year, month)[1] + 1):
                    if present_days_count >= rec.present_days:
                        break

                    day_date = fields.Date.from_string(f"{year}-{month:02d}-{day:02d}")
                    day_of_week = day_date.weekday()

                    if day_of_week in (5, 6):
                        continue
                    attendance_periods = []

                    first_entry_hours_from = None
                    last_entry_hours_to = None

                    for attendance in rec.employee_id.resource_calendar_id.attendance_ids:
                        if int(attendance.dayofweek) == day_of_week:
                            if first_entry_hours_from is None or attendance.hour_from < first_entry_hours_from:
                                first_entry_hours_from = attendance.hour_from
                            
                            if last_entry_hours_to is None or attendance.hour_to > last_entry_hours_to:
                                last_entry_hours_to = attendance.hour_to

                    if first_entry_hours_from is not None and last_entry_hours_to is not None:
                        check_in = fields.Datetime.from_string(f"{year}-{month:02d}-{day:02d}").replace(
                            hour=int(first_entry_hours_from),
                            minute=int((first_entry_hours_from % 1) * 60),
                            second=0
                        ) - timedelta(hours=5)
                        
                        check_out = fields.Datetime.from_string(f"{year}-{month:02d}-{day:02d}").replace(
                            hour=int(last_entry_hours_to),
                            minute=int((last_entry_hours_to % 1) * 60),
                            second=0
                        ) - timedelta(hours=5)

                        existing_attendance = attendance_model.search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('check_in', '<=', check_out),
                            ('check_out', '>=', check_in)
                        ], limit=1)

                        if not existing_attendance:
                            attendance_model.create({
                                'employee_id': rec.employee_id.id,
                                'check_in': check_in,
                                'check_out': check_out,
                            })
                            present_days_count += 1




    def write(self, vals):
        res = super(ImportAttendance, self).write(vals)
        if 'present_days' in vals:
            self._create_attendance_records()
        return res

    @api.model
    def create(self, vals):
        record = super(ImportAttendance, self).create(vals)
        if 'present_days' in vals:
            record._create_attendance_records()
        return record

    @api.depends('year', 'month')
    def _compute_total_days(self):
        for rec in self:
            if rec.year and rec.month:
                year = int(rec.year)
                month = list(dict(self._fields['month'].selection).keys()).index(rec.month) + 1
                rec.total_days = calendar.monthrange(year, month)[1]
            else:
                rec.total_days = 0


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.job_id = rec.employee_id.job_id.id
                rec.emp_id = rec.employee_id.employee_id