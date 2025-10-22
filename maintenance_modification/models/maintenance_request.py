# from odoo import models,api,fields,_
# from odoo.exceptions import UserError

# class MaintenanceRequest(models.Model):
#     _inherit = "maintenance.request"
#     maintenance_type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive'),('others','Others')], string='Maintenance Type', default="corrective")
#     priority = fields.Selection([('0', 'Emergency'), ('1', 'Urgent'), ('2', 'Normal'), ('3', 'Shut Down')], string='Priority')


#     discipline_id = fields.Many2one("discipline",string="Discipline")
    
#     job_assignment = fields.Many2many(
#         'res.users')
    
#     team_member_ids = fields.Many2many(
#         'res.users', compute='_compute_team_members', store=False
#     )

#     job_duration =  fields.Float(string="Job Duration")

#     @api.depends('maintenance_team_id')
#     def _compute_team_members(self):
#         for record in self:
#             record.team_member_ids = record.maintenance_team_id.member_ids

#     job_performer_remarks = fields.Text("Job Performer Remarks")
#     job_requester_remarks = fields.Text("Job Requester Remarks")
#     equipment_id =  fields.Many2one("maintenance.equipment",string="Equipment")

#     functional_loc = fields.Char(string="Functional Location")
    
    

#     @api.onchange("equipment_id")
#     def populate_functional_location(self):
#         for rec in self:
#             if rec.equipment_id:
#                 rec.functional_loc = f"{rec.equipment_id.name} {rec.equipment_id.functional_location.location_name if rec.equipment_id.functional_location else ''}"

#             else:
#                 rec.functional_loc = ""



from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import datetime

class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"





    department_id = fields.Many2one("hr.department", string="Department")
    cost_center = fields.Many2one(
        "account.analytic.account",
        string="Cost Center",
        related="equipment_id.cost_center",
        store=True
    )


    maintenance_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('others', 'Others')
    ], string='Maintenance Type', default="corrective")
    description  = fields.Char(string="Description")
    fault_category_id = fields.Many2one("fault.category", string="Fault Category")

    priority = fields.Selection([
        ('0', 'Emergency'),
        ('1', 'Urgent'),
        ('2', 'Normal'),
        ('3', 'Shut Down')
    ], string='Priority')

    discipline_id = fields.Many2one("discipline", string="Discipline")

    job_assignment = fields.Many2many('hr.employee')

    team_member_ids = fields.Many2many(
        'hr.employee', compute='_compute_team_members', store=False,compute_sudo=True
    )

    job_duration = fields.Float(string="Job Duration")

    wr_no = fields.Char(string="W.R No", readonly=True, copy=False, default="New")

    job_performer_remarks = fields.Text("Job Performer Remarks")
    job_requester_remarks = fields.Text("Job Requester Remarks")
    equipment_id = fields.Many2one("maintenance.equipment", string="Equipment")

    functional_loc = fields.Char(string="Functional Location")

    is_in_equipment_group = fields.Boolean(
        string="Is Clickable",
        compute="_compute_is_clickable",

    )

    frequency = fields.Selection(selection="_get_frequency", string="Frequency")

    remarks =  fields.Text(string="Remarks")

    def _get_frequency(self):
        options = [('daily', 'Daily'),
                        ('weekly', 'Weekly'),
                        ('fortnightly', 'Fortnightly'),
                        ('monthly', 'Monthly'),
                        ('quarterly', 'Quarterly'),
                        ('half_yearly', 'Half Yearly'),
                        ('yearly', 'Yearly')
                        ]
        for rec in self:
            options = []
            if rec.equipment_id and rec.equipment_id.discipline_line_ids:
                for line in rec.equipment_id.discipline_line_ids:
                    if line.frequency not in options:
                        options.append((line.frequency.lower(), line.frequency))

        return options

    @api.depends("stage_id")
    def _compute_is_clickable(self):
        equipment_group = self.env.ref('maintenance.group_equipment_manager', raise_if_not_found=False)
        for record in self:
            record.is_in_equipment_group = self.env.user.id in equipment_group.users.ids if equipment_group else False



    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if not self.is_in_equipment_group:
            raise UserError("You do not have permission to change the stage. Please contact your administrator.")


    @api.depends('maintenance_team_id')
    def _compute_team_members(self):
        for record in self:
            record.team_member_ids = record.maintenance_team_id.emp_ids

    @api.onchange("equipment_id")
    def populate_functional_location(self):
        for rec in self:
            if rec.equipment_id:
                rec.functional_loc = f"{rec.equipment_id.functional_location.location_name if rec.equipment_id.functional_location else ''} {'-'if  rec.equipment_id.functional_location and rec.equipment_id.x_studio_equipment_id_1 else ''} {rec.equipment_id.x_studio_equipment_id_1}"
            else:
                rec.functional_loc = ""

    @api.model
    def create(self, vals):
        # if vals.get('wr_no', 'New') == 'New':
        #     # Get the current date for Month-Year format
        #     current_date = datetime.now()
        #     month_year = current_date.strftime('%B-%Y')
        #     # Get the last W.R No and calculate the next number
        #     last_record = self.search([], order="id desc", limit=1)
        #     next_number = 1  # Default to 1 if no valid W.R No exists

        #     if last_record and last_record.wr_no:
        #         try:
        #             # Extract and increment the last number
        #             last_number = int(last_record.wr_no.split(':')[1].split('-')[0].strip())
        #             next_number = last_number + 1
        #         except (IndexError, ValueError):
        #             # Handle cases where the W.R No format is incorrect
        #             next_number = 1
        if vals.get('wr_no', 'New') == 'New':
            wr_no = self.env['ir.sequence'].next_by_code('wr_no_sequence.code')
                # Generate the new W.R No
            vals['wr_no'] = wr_no
            # raise UserError(str(vals))
        return super(MaintenanceRequest, self).create(vals)


    def name_get(self):
        result = []
        for rec in self:
            name = rec.wr_no
            result.append((rec.id, name))
        return result

