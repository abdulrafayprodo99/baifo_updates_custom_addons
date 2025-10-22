from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime


# Bilal

class StockPicking(models.Model):
    _inherit= "stock.picking"

    draft_name = fields.Char(string="Draft Name")
    is_draft_sequence = fields.Boolean(string="Is Draft Sequence",related="picking_type_id.is_draft_sequence")
    
    
    @api.model_create_multi
    def create(self, vals_list):
        pickings = super(StockPicking,self).create(vals_list)
        for res in pickings:
            defaults = self.default_get(['name', 'picking_type_id'])
            picking_type = self.env['stock.picking.type'].browse(res['picking_type_id']['id'])
            if picking_type.is_draft_sequence:
                res.write({
                    'name': 'Draft' + '/' + str(res.id)
                })
            else:
                res.write({
                    'name': res.picking_type_id.sequence_id.next_by_id()
                })
            #     res['name'] = picking_type.sequence_id.next_by_id()
            
        return pickings
        
               
    #     return pickings
    

    # def button_validate(self):
    #     pickings = super(StockPicking,self).button_validate()
    #     for rec in self:
    #         if rec.state == 'done':
    #             rec['name'] = rec.picking_type_id.sequence_id.next_by_id()
                
    #         # if rec.picking_type_id.is_draft_sequence:
    #             # rec['name'] = 'Draft' + '/' + str(rec.id)
                
    #         # else:
                
    #             # rec['name'] = 'Draft' + '/' + str(rec.id)
            
    #     return pickings



class StockPickingType(models.Model):
    _inherit="stock.picking.type"


    is_draft_sequence = fields.Boolean(string="Is Draft Sequence", store=True)
    is_grn_approval = fields.Boolean(string="Is GRN Approval", store=True)
    is_rtn_approval = fields.Boolean(string="Is RTN Approval", store=True)

class StockMove(models.Model):
    _inherit = "stock.move"



    @api.depends('picking_id', 'name', 'picking_id.name','picking_id.state')
    def _compute_reference(self):
        for move in self:
            move.reference = move.picking_id.name
            move._prepare_common_svl_vals()





class StockValuation(models.Model):
    _inherit="stock.valuation.layer"

    # description = fields.Char('Description', readonly=True, compute="compute_description")
    description = fields.Char('Description', readonly=True)


    # @api.depends('stock_move_id')
    # def compute_description(self):

    #     for rec in self:
    #         for line_c in rec.stock_move_id:
    #             rec['description'] = str(line_c.reference) +" "+ str(line_c.product_id.name)
    #             svl = self.stock_valuation_layer_id.stock_move_id
    #             rec.account_move_id.ref =  rec.stock_move_id.reference
    #             for line in rec.account_move_id.line_ids:
    #                 line['name'] = str(self.stock_move_id.reference) +" "+ str(self.product_id.name)
    #         # raise UserError(rec.account_move_id)
            # rec.account_move_line_id.name = str(self.stock_move_id.reference) +" "+ str(self.product_id.name)
            
    
    