# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
class QualityCheck(models.Model):
    _inherit = 'quality.check'




    qir_created=fields.Boolean("Created Qir")
    

    def action_create_qir(self):
        active_ids = self.env.context.get('active_ids', [])
        checks=self.browse(active_ids)
        first_check_model = checks[0].team_id
        if not all(check.team_id == first_check_model for check in checks):
            raise UserError('All the selected records must be of the same type.')

        doc_ref,doc_type=(checks[0].production_id,"mo") if checks[0].production_id else  (checks[0].picking_id,"grn") if checks[0].picking_id else (False,False)
        product=checks[0].product_id.id 
        partner=checks[0].partner_id.id 
        team=checks[0].team_id.id 
        lines_data = []
        for line in checks:
            if line.qir_created==False:
                line.qir_created=True
                min_val = round(line.tolerance_min, 2)
                max_val = round(line.tolerance_max, 2)
                measure = round(line.measure, 2)
                lines_data.append((0, 0, {
                    'point_id': line.point_id.id,
                    'quality_title': line.point_id.title,
                    'standards': f"{min_val}-{max_val}",
                    'result': str(measure),
                    'qc_id': line.id
                }))
            else:
                raise UserError(f"{line.name} has it's QIR already Created")
        

        if doc_type =="mo":
            date=doc_ref.move_raw_ids[0].move_date if doc_ref.move_raw_ids else False
            # lot_id=doc_ref.lot_producing_id.id
        elif doc_type =="grn":
            date=doc_ref.date_done if doc_ref.date_done else False
            # lot_name=doc_ref.move_line_ids[0].lot_name if doc_ref.move_line_ids else False
            # if lot_name:
            #     lot_id=self.env['stock.lot'].search([('name','=',lot_name)],limit=1)
            #     if lot_id:
            #         lot_id=lot_id.id
            #     else:
            #         lot_id=False
            # else:
            #     lot_id=False

            
        else:
            date=False
        


        qir = self.env['rqi.model'].create({
                'name': self.env['ir.sequence'].next_by_code('qir.sequence'),
                'product_id': product,
                'partner_id': partner,
                'team_id': team,
                # 'lot_id': lot_id,
                'line_id': lines_data,
                'doc_date':date,
                'doc_refrence': doc_ref.name,
                'doc_id':doc_ref.id,
                # doc_type:doc_ref.id,
                'ref_type':doc_type
            })

        return qir
         
                