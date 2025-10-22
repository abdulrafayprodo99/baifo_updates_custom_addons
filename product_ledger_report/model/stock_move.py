from odoo import models,api,fields
from odoo.exceptions import UserError
from datetime import datetime,timedelta


class StockMove(models.Model):
    _inherit = "stock.move"

    move_date = fields.Datetime(string="Move Date",compute="_compute_final_date",store=True)


    @api.depends('production_id','date','state')
    def _compute_final_date(self):
        for rec in self:
            rec.move_date = rec.date
            if rec.stock_valuation_layer_ids:
                rec.move_date = rec.stock_valuation_layer_ids[-1].move_date_filter
            
            

class StockMoveLine(models.Model):
    _inherit="stock.move.line"

    move_date = fields.Datetime(string="Move Date",related="move_id.move_date",store=True)



class StockValuation(models.Model):
    _inherit= "stock.valuation.layer"


    product_type_detailed= fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')
    ],'Product Type Detailed',compute="_compute_product_type")
    product_type_filter= fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')
    ],'Product Type Detailed')
    # move_date=fields.Datetime("Move Date Compute")
    move_date_filter=fields.Datetime('Move Date',compute="_compute_move_date",store=True)


    def _compute_product_type(self):
        for rec in self:
            rec.product_type_detailed=rec.product_id.detailed_type
            rec.product_type_filter=rec.product_id.detailed_type


    @api.depends('stock_move_id','account_move_id.date','stock_valuation_layer_id')
    def _compute_move_date(self):
        for rec in self:
            if rec.stock_move_id:
                # rec.move_date=rec.stock_move_id.move_date
                rec.move_date_filter=rec.stock_move_id.move_date
            elif rec.stock_valuation_layer_id:
                # rec.move_date=rec.stock_valuation_layer_id.stock_move_id.move_date
                rec.move_date_filter=rec.stock_valuation_layer_id.stock_move_id.move_date
            else:
                # rec.move_date=rec.create_date
                rec.move_date_filter=rec.create_date
            if rec.account_move_id and rec.account_move_id != rec.account_move_id.date:
                # rec.move_date = rec.account_move_id.date
                rec.move_date_filter = rec.account_move_id.date