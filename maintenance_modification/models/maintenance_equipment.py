from odoo import models, api, fields
from odoo.exceptions import UserError

class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    sr_no = fields.Integer(string="Sr No.")
    functional_location = fields.Many2one("functional.location", string="Functional Location")


    machine_history_ids =  fields.One2many('maintenance.request','equipment_id',string="Machine History",compute="_compute_machine_history",store=True)

    
    def _compute_machine_history(self):
        ids = []
        for rec in self:
            if rec.equipment_id:
                requests = self.env['maintenance.request'].search([('equipment_id', '=', rec.equipment_id.id)])
                ids = [(4, request.id) for request in requests]

            rec.machine_history_ids = ids
    equipment_id = fields.Char(string="Equipment")
    equipment_func_name = fields.Char(string="Equipment Functional Name")

    department_id = fields.Many2one("hr.department", string="Department")
    cost_center = fields.Many2one(
        "account.analytic.account", 
        string="Cost Center", 
        domain="[('plan_id.parent_id', '=', 108)]"
    )



    asset_tag_no = fields.Many2one("account.asset", string="Asset Name")
    asset_tag_name = fields.Char(string="Asset Tag No", readonly=True )
    discipline_line_ids = fields.One2many('discipline.line', 'maintenance_equipment_id')


    @api.onchange('asset_tag_no')
    def populate_asset_tag_name(self):
        for rec in self:
            if rec.asset_tag_no:
                rec.asset_tag_name = rec.asset_tag_no.asset_tag
            else:
                rec.asset_tag_name = ""




class DisciplineLine(models.Model):
    _name = 'discipline.line'
    _description = 'Discipline Line'

    discipline_id = fields.Many2one('discipline', string='Discipline', required=True)
    name = fields.Char(string="Discipline", readonly=True)

    @api.onchange('discipline_id')
    def _onchange_discipline_id(self):
        if self.discipline_id:
            self.name = self.discipline_id.name_des
        else:
            self.name = ''
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
    ], string='Frequency', required=True)

    components = fields.Char(string="Components")
    action_required = fields.Boolean(string='Action Required')
    remarks = fields.Text(string='Remarks')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string='Maintenance Equipment')
