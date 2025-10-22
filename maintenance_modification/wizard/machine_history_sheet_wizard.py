from odoo import models,api,fields,_
from odoo.exceptions import UserError
import json
class MachineHistorySheetWizard(models.TransientModel):
    _name = 'machine.history.sheet.wizard'
    _description = 'Machine History Sheet Wizard'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
 
    def button_export_pdf(self):
        self.ensure_one()
        if not self.equipment_id:
            raise UserError(_('Please select an equipment.'))
        requests = self.env['maintenance.request'].search([('equipment_id', '=', self.equipment_id.id)])
        if self.start_date:
            requests = requests.filtered(lambda r: r.request_date >= self.start_date)
        if self.end_date:
            requests = requests.filtered(lambda r: r.request_date <= self.end_date)
        filtered_requests = []
        for req in requests:
            assignees = []
            if req.job_assignment:
                for assignee in req.job_assignment:
                    assignees.append(assignee.name)
            filtered_requests.append({
                "schedule" :req.schedule_date,
                "wr_no":req.wr_no,
                "description":req.description,
                "x_studio_job_start_time":req.x_studio_job_start_time,
                "x_studio_job_end_time":req.x_studio_job_end_time,
                "x_studio_rectification_action_1":req.x_studio_rectification_action_1,
                "job_assignment":assignees,
                "job_performer_remarks":req.job_performer_remarks,
            })

        data = {
            'doc_ids': self.id,
            'doc_model': 'machine.history.sheet.wizard',
            'requests': filtered_requests
        }

        return self.env.ref('maintenance_modification.btn_report_machine_history_sheet').report_action(self, data=data)

    