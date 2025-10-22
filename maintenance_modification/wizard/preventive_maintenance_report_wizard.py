from odoo import models,api,fields,_
from odoo.exceptions import UserError
from datetime import datetime,date
import calendar

import json
class PreventiveMaintenanceReportWizard(models.TransientModel):
    _name = 'preventive.maintenance.report.wizard'
    _description = 'Preventive Maintenance Report Wizard'

    month = fields.Date(string='Month')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    team = fields.Many2one(
        'maintenance.team',
        string='Team',
        help='Select a team to filter the requests by the team responsible for the equipment.'
    )
    stage_id = fields.Many2one(
        'maintenance.stage',
        string='Stage',
    )
    stage_track=fields.Boolean('All Stages',default=True)

    
    def get_first_and_last_dates(self):

        date_obj = self.month
        first_date = date_obj.replace(day=1)
        last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
        last_date = date_obj.replace(day=last_day)
        return first_date, last_date

    def button_export_pdf(self):
        self.ensure_one()
        stage=('stage_id', '!=', False) if self.stage_track else ('stage_id', '=', self.stage_id.id)
        requests = self.env['maintenance.request'].search([('maintenance_type','=','preventive'),
        ('equipment_id', '!=',False),
        # ('x_studio_related_field_ctShs.user_id','=',self.env.user.id),
        ('schedule_date', '!=',False),
        ('maintenance_team_id', '=', self.team.id),
        stage,
        ])
        if not self.date_from and self.date_to:
            raise UserError("Please select dates.")
        # start_date,end_date = self.get_first_and_last_dates()
        requests = requests.filtered(lambda r: r.schedule_date.date() >= self.date_from and r.schedule_date.date() <= self.date_to)
        total_due = 0
        total_done = 0
        filtered_requests = []
        for req in requests:
            if req.stage_id.name.lower() == 'completed':
                total_done += 1
            else:
                total_due += 1
            request_date = req.request_date if req.request_date else None  # Keep as date object            
            filtered_requests.append({
                "job":req.name,
                'wr_no':req.wr_no,
                "equipment":req.equipment_id.name,
                "area" :req.equipment_id.functional_location.x_studio_location_name if req.equipment_id.functional_location else '',
                "functional_location":req.functional_loc,   
                "proposed_date":req.schedule_date.date() if req.schedule_date else None,
                "execution_date":req.schedule_date.date() if req.schedule_date and req.stage_id.name == 'Completed' else None,
                'status':req.stage_id.name if req.stage_id.name == 'Completed' else 'Pending',
                "job_performer_remarks":req.job_performer_remarks,
            })

        filtered_requests = sorted(
                    filtered_requests,
                    key=lambda k: k['proposed_date'] if isinstance(k['proposed_date'], date) else date.min
                )
        for req in filtered_requests:
            if req['execution_date']:
                req['execution_date'] = req['execution_date'].strftime('%Y-%m-%d').upper()
            if req['proposed_date']:
                req['proposed_date'] = req['proposed_date'].strftime('%Y-%m-%d').upper()
        total_compliance = 0
        try:
            total_compliance = (total_done/(total_due+total_done)) * 100
        except :
            total_compliance = 0
        data = {
            'doc_ids': self.id,
            'team': self.team.name,
            'doc_model': 'preventive.maintenance.report.wizard',
            'requests': filtered_requests,
            'total_due':total_due + total_done,
            'total_done':total_done,
            'total_compliance': total_compliance,
            'month':f"{ self.date_from.strftime('%Y-%m-%d').upper()}  to  { self.date_to.strftime('%Y-%m-%d').upper()}",
        }
        return self.env.ref('maintenance_modification.btn_report_preventive_maintenance_report').report_action(self, data=data)

    