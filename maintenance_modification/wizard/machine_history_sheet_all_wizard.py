from odoo import models,api,fields,_
from odoo.exceptions import UserError
import json
from datetime import datetime,date
class MachineHistorySheetWizardAll(models.TransientModel):
    _name = 'machine.history.sheet.wizard.all'
    _description = 'Machine History Sheet Wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    team = fields.Many2one(
        'maintenance.team',
        string='Team',
        help='Select a team to filter the requests by the team responsible for the equipment.'
    )
    stage_id = fields.Many2one(
        'maintenance.stage',
        string='Stage',
    )
    # maintenance_type = fields.Selection(
    #     [('corrective', 'Corrective'),
    #      ('preventive', 'Preventive'),
    #      ('others', 'Others')],
    #     string='Maintenance Type',
    #     default='corrective',  # Set default value if needed
    # )
 
    def button_export_pdf(self):
        self.ensure_one()
        requests = self.env['maintenance.request'].search([('equipment_id', '!=',False),
         ('maintenance_team_id', '=', self.team.id),
         ('stage_id', '=', self.stage_id.id),
        #  ('maintenance_type', '=', self.maintenance_type),
         ])
        if self.start_date:
            requests = requests.filtered(lambda r: r.schedule_date and r.schedule_date.date() >= self.start_date)
        if self.end_date:
            requests = requests.filtered(lambda r: r.schedule_date and r.schedule_date.date() <= self.end_date)

        
        filtered_requests = []
        min_date = None
        max_date = None
        total_due = 0
        total_done = 0
        for req in requests:
            if req.x_studio_job_start_time:
                    min_date = req.x_studio_job_start_time if req.x_studio_job_start_time else None
            if req.x_studio_job_end_time:
                    max_date = req.x_studio_job_end_time if req.x_studio_job_end_time else None
            if req.stage_id.name.lower() == 'completed':
                total_done += 1
            else:
                total_due += 1
            schedule = req.schedule_date.date() if req.schedule_date else None  # Keep as date object
            # if min_date is None or (schedule and schedule < min_date):
            #     min_date = schedule
            # if max_date is None or (schedule and schedule > max_date):
            #     max_date = schedule
            
            
            filtered_requests.append({
                "schedule" :schedule.strftime('%Y-%m-%d').upper() if schedule else '',
                "wr_no":req.wr_no,
                "genre":req.maintenance_type.capitalize() if req.maintenance_type else '',   
                "job":req.name,
                'start_date':min_date,
                'end_date':max_date ,
                "description":req.description,
                "equipment":req.equipment_id.name,
                "functional_location":req.functional_loc if req.functional_loc else '',
                "x_studio_rectification_action_1":req.x_studio_rectification_action_1,
                "status":req.stage_id.name if req.stage_id else '',
                "job_performer_remarks":req.job_performer_remarks,
            })
            
        filtered_requests = sorted(
                filtered_requests,
                key=lambda k: datetime.strptime(k['schedule'], "%Y-%m-%d").date()
                if isinstance(k['schedule'], str) and k['schedule'].strip() else date.min
            )
        data = {
            'doc_ids': self.id,
            'team': self.team.name,
            'doc_model': 'machine.history.sheet.wizard.all',
            'requests': filtered_requests,
            'start_date':min_date,
            'end_date':max_date ,
            'total_due':total_due + total_done,
            'total_done':total_done,
            'range_date':f"{ self.start_date.strftime('%Y-%m-%d').upper() if self.start_date  else str(min_date)}  to  { self.end_date.strftime('%Y-%m-%d').upper() if self.end_date else str(max_date)}",
        }
        return self.env.ref('maintenance_modification.btn_report_machine_history_sheet_all').report_action(self, data=data)

    