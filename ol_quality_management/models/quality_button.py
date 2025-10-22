# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'
    qr_count = fields.Integer(string='QIR Count', compute='_compute_qr_count')
    qr_count_draft = fields.Integer(string='QIR Count', compute='_compute_qr_count_in_draft')


    def _compute_qr_count(self):
        for team in self:
            # Count the number of QIRs associated with this team
            qir_count = self.env['rqi.model'].search_count([('team_id', '=', team.id)])
            team.qr_count = qir_count


    def _compute_qr_count_in_draft(self):
        for team in self:
            # Count the number of QIRs associated with this team
            qr_count_draft = self.env['rqi.model'].search_count([('team_id', '=', team.id), ('state_approval', '=', 'draft')])
            team.qr_count_draft = qr_count_draft


    def action_quality_alert_button_draft(self):
        for team in self:
            # Fetch QIRs where team_id matches team_ids in the quality.alert.team record
            qirs = self.env['rqi.model'].search([('team_id', '=', team.id), ('state_approval', '=', 'draft')])

            # Check if QIRs were found
            if qirs:

                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Related QIRs',
                    'res_model': 'rqi.model',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', qirs.ids)],  # Filter QIRs based on the team_id
                    'context': {},
                }

    def action_quality_alert_button(self):
        for team in self:
            # Fetch QIRs where team_id matches team_ids in the quality.alert.team record
            qirs = self.env['rqi.model'].search([('team_id', '=', team.id)])

            # Check if QIRs were found
            if qirs:

                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Related QIRs',
                    'res_model': 'rqi.model',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', qirs.ids)],  # Filter QIRs based on the team_id
                    'context': {},
                }
    



class QualityCheck(models.Model):
    _inherit = 'quality.check'
                         

        
    # def action_create_qir(self):
    #     active_ids = self.env.context.get('active_ids', [])
    #     checks = self.browse(active_ids)
    #     raise UserError(f"{checks}")

    #     result_dict = {}

    #     for rec in checks:
    #         key = f"{rec.x_studio_purchase_order},{rec.product_id.id},{rec.team_id.id},{rec.partner_id.id}"
    #         if key not in result_dict:
    #             result_dict[key] = []
    #         result_dict[key].append(rec)

    #     created_qirs = []

    #     def safe_int(val):
    #         return False if val == 'False' else int(val)

    #     for key, items in result_dict.items():
    #         split_data = key.split(',')
    #         lines_data = []

    #         for line in items:
    #             min_val = round(line.tolerance_min, 2)
    #             max_val = round(line.tolerance_max, 2)
    #             measure = round(line.measure, 2)
    #             lines_data.append((0, 0, {
    #                 'point_id': line.point_id.id,
    #                 'quality_title': line.point_id.title,
    #                 'standards': f"{min_val}-{max_val}",
    #                 'result': str(measure),
    #                 'qc_id': line.id
    #             }))

    #         purchase_order = self.env['purchase.order'].search([('name', '=', split_data[0])], limit=1)
    #         qir = self.env['rqi.model'].create({
    #             'name': self.env['ir.sequence'].next_by_code('qir.sequence'),
    #             'product_id': safe_int(split_data[1]),
    #             'partner_id': safe_int(split_data[3]),
    #             'team_id': safe_int(split_data[2]),
    #             'lot_id': False,
    #             'line_id': lines_data,
    #             'doc_date': purchase_order.date_order.date() if purchase_order else datetime.today(),
    #             'doc_refrence': split_data[0]
    #         })

    #         created_qirs.append(qir)

    #     return created_qirs

