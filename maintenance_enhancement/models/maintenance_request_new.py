from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MaintenanceRequestEnhancement(models.Model):
    _inherit = "maintenance.request"

    job_completed_by = fields.Many2one(
        'hr.employee', string="Job Completed By", compute="_compute_job_completed_by", store=True
    )
    job_completed_date = fields.Datetime(
        string="Job Completed Date", compute="_compute_job_completed_by", store=True
    )

    approved_by = fields.Many2one(
        'res.users', string="Approved By", compute="_compute_approved_by", store=True
    )
    approved_date = fields.Datetime(
        string="Approved Date", compute="_compute_approved_by", store=True
    )

    request_by = fields.Many2one(
        'res.users', string="Requested By", compute="_compute_request_by", store=True, default=lambda self: self.env.user
    )
    requested_date = fields.Datetime(
        string="Requested Date", compute="_compute_request_by", store=True
    )

    @api.depends('stage_id')
    def _compute_approved_by(self):
        for record in self:
            if record.stage_id and record.stage_id.name == 'Completed':
                record.approved_by = self.env.user
                record.approved_date = fields.Datetime.now()
            else:
                record.approved_by = False
                record.approved_date = False

    @api.depends('job_assignment', 'stage_id')
    def _compute_job_completed_by(self):
        for record in self:
            if record.stage_id and record.stage_id.name == 'Completed' and record.job_assignment:
                record.job_completed_by = record.job_assignment[0]
                record.job_completed_date = fields.Datetime.now()
            else:
                record.job_completed_by = False
                record.job_completed_date = False

    @api.depends('create_uid')
    def _compute_request_by(self):
        for record in self:
            record.request_by = record.create_uid
            record.requested_date = record.create_date
