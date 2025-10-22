# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    rqi_count = fields.Integer(
        'Quality Issue Count',
        compute='_compute_rqi_count'
    )
    prepare_visible=fields.Boolean("Prepare Visibility",compute="_compute_visible")

    @api.depends('check_ids')
    def _compute_visible(self):
        for rec in self:
            if  rec.check_ids:
                rec.prepare_visible=True if len(self.env['rqi.model'].search([('mo','=',rec.id)]))>0 else False
            else:
                rec.prepare_visible=True 

    
    def _compute_rqi_count(self):
        for mo in self:
            mo.rqi_count = self.env['rqi.model'].search_count([
                '|',
                '&',
                    ('doc_id', '=', mo.id),
                    ('ref_type', '=', 'mo'),
                ('doc_refrence', '=', mo.name)
            ])

    def action_view_rqi_records(self):
        self.ensure_one()
        return {
            'name': ('QIR'),
            'type': 'ir.actions.act_window',
            'res_model': 'rqi.model',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                '&',
                    ('doc_id', '=', self.id),
                    ('ref_type', '=', 'grn'),
                ('doc_refrence', '=', self.name)
            ],
            'context': {
                'default_doc_refrence': self.name,
                'create': False
            },
            'target': 'current',
        }
