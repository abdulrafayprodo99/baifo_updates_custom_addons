# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
class StockPicking(models.Model):
    _inherit = 'stock.picking'


    rqi_count = fields.Integer(
        'Quality Issue Count',
        compute='_compute_rqi_count'
    )

    prepare_visibility=fields.Boolean("Visiblity of prepare",compute="_compute_prepare_visibility")

    todo_count=fields.Integer("Todo Count",compute="_compute_counts")
    pass_count=fields.Integer("Pass Count",compute="_compute_counts")
    fail_count=fields.Integer("Fail Count",compute="_compute_counts")
    checks=fields.Boolean("Check",compute="_compute_check_count")

    def _compute_prepare_visibility(self):
        for rec in self:
            if rec.check_ids :
                flag=self.env['rqi.model'].search([
                '|', 
                '&', 
                ('doc_id', '=', self.id), 
                ('ref_type', '=', 'grn'),
                ('doc_refrence', '=', self.name)
            ],limit=1)
                if flag:
                    rec.prepare_visibility= True if flag.state_approval =='approve' else False
                else:
                    rec.prepare_visibility=False
            else:
                rec.prepare_visibility=True



    def _compute_check_count(self):
        for rec in self:
            if len(rec.check_ids)>0:
                rec.checks=True 
            else:
                rec.checks=False


    def check_availabilty(self):
        for rec in self:
            raise UserError("123457890")




    @api.depends("check_ids")
    def _compute_counts(self):
        for rec in self:
            rec.todo_count=len(rec.check_ids.filtered(lambda check : check.quality_state=='none'))
            rec.pass_count=len(rec.check_ids.filtered(lambda check : check.quality_state=='pass'))
            rec.fail_count=len(rec.check_ids.filtered(lambda check : check.quality_state=='fail'))


    def action_open_quality_check_picking_todo(self):
        action = {
        "type": "ir.actions.act_window",
        "res_model": "quality.check",
        "domain": [('picking_id', '=', self.id), ('quality_state', '=', 'none')],
        "context": {"create": False},
        "name": "Quality Checks",
        'view_mode': 'tree,form',}

        return action
    def action_open_quality_check_picking_pass(self):
        action = {
        "type": "ir.actions.act_window",
        "res_model": "quality.check",
        "domain": [('picking_id', '=', self.id), ('quality_state', '=', 'pass')],
        "context": {"create": False},
        "name": "Quality Checks",
        'view_mode': 'tree,form',}

        return action
    def action_open_quality_check_picking_fail(self):
        action = {
        "type": "ir.actions.act_window",
        "res_model": "quality.check",
        "domain": [('picking_id', '=', self.id), ('quality_state', '=', 'fail')],
        "context": {"create": False},
        "name": "Quality Checks",
        'view_mode': 'tree,form',}

        return action

    
    
    def _compute_rqi_count(self):
        for picking in self:
            picking.rqi_count = self.env['rqi.model'].search_count([
                '|',
                '&',
                    ('doc_id', '=', picking.id),
                    ('ref_type', '=', 'grn'),
                ('doc_refrence', '=', picking.name)
        ])
    def action_view_rqi_records(self):
        self.ensure_one()
        return {
            'name': ('QIR'),
            'type': 'ir.actions.act_window',
            'res_model': 'rqi.model',
            'view_mode': 'tree,form',
            # 'domain': [('doc_refrence', '=', self.name)],
            'domain': [   '|', 
                            '&',  
                    ('doc_id', '=', self.id),
                    ('ref_type', '=', 'grn'),
                ('doc_refrence', '=', self.name)],
            'context': {
                'default_doc_refrence': self.name,
                'create': False
            },
            'target': 'current',
        }
    
    def write(self, vals):
        res = super(StockPicking, self).write(vals)


        if self.move_line_ids:

            if 'location_id' in vals or 'location_dest_id' in vals:

                location_id = vals.get('location_id', self.location_id.id)
                location_dest_id = vals.get('location_dest_id', self.location_dest_id.id)
                self.move_line_ids.write({
                        'location_id': location_id,
                        'location_dest_id': location_dest_id
                    })
        if self.move_ids:
            if 'location_id' in vals or 'location_dest_id' in vals:
                location_id = vals.get('location_id', self.location_id.id)
                location_dest_id = vals.get('location_dest_id', self.location_dest_id.id)
                self.move_ids.write({
                        'location_id': location_id,
                        'location_dest_id': location_dest_id
                    })

        return res


    def action_prepare2(self):
        
        res = super(StockPicking,self).action_prepare2()
        qir=self.env['rqi.model'].search([
            ('doc_id','=',self.id),
            ('ref_type','=','grn')])
        if qir:
            qir.doc_refrence=self.name

        return res
    
    @api.constrains("backorder_id")
    def create_back_order_quality_checks(self):
        for rec in self:
            if rec.backorder_id:
                for check in rec.backorder_id.check_ids:
                        self.env['quality.check'].create({
                            'picking_id': self.id,  # Link the quality check to the new back order
                            'product_id': check.product_id.id,  # Product being checked
                            'quality_state': 'none',  # Initial state, it could be different based on your needs
                            'x_studio_purchase_order':check.x_studio_purchase_order,
                            'point_id':check.point_id.id,
                            'title':check.title,
                            'test_type_id':check.test_type_id.id,
                            'measure_on':check.measure_on,
                            'team_id':check.team_id.id,
                            'partner_id':check.partner_id.id,
                            'tolerance_min':check.tolerance_min,
                            'tolerance_max':check.tolerance_max,
                        
                        })

        return True

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    gross_wgt=fields.Float("Gross Weight")
    available_qty=fields.Float("Available Quantity",compute="available_qty_computed")

    @api.depends('lot_id')
    def available_qty_computed(self):
        for rec in self:
            record=self.env['stock.quant'].search([
                ('lot_id','=',rec.lot_id.id),
                ('location_id','=',rec.location_id.id),
                ('product_id','=',rec.move_id.product_id.id)
                ],limit=1)
            rec.available_qty=record.available_quantity

    # @api.onchange("location_dest_id","location_id")
    # def location_restrictions(self):
    #     for rec in self:
    #         if rec.picking_id.picking_type_id.id !=2:  
    #             if rec.location_dest_id or rec.location_id:
    #                 raise UserError("You Can't Changed Location From Lines Kindly Configure it From Transfer Form")   



class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_view_product_details(self):
        return self.product_id.action_update_quantity_on_hand()


  