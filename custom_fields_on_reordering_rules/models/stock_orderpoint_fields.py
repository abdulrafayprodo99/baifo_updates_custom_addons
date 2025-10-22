from odoo import models, fields, api

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    # Float fields
    reorder_level = fields.Float(string='Reorder Level', compute='_compute_reorder_level')
    final_safety_stock_level = fields.Float(string='Final Safety Stock Level', compute='_compute_final_safety_stock_level',readonly=False,store=True)
    max_lead_time = fields.Float(string='Max Lead Time')
    avg_lead_time = fields.Float(string='Average Lead Time',compute="_compute_avg_lead_time")
    min_lead_time = fields.Float(string='Minimum Lead Time')
    max_consumption = fields.Float(string='Max Consumption')
    avg_consumption = fields.Float(string='Average Consumption')
    current_stock = fields.Float(string='Current Stock')



        # New field for onhand quantity
    onhand = fields.Float(
        string='On Hand Quantity',
        related='product_id.qty_available',
        store=True,  # Use store=True to make it searchable and storable in the database
        readonly=True
    )

    forecast_quantity = fields.Float('Forecast', readonly=True, compute="_compute_forecast_qty" , digits='Product Unit of Measure')
    # @api.depends('product_id', 'location_id', 'product_id.stock_move_ids', 'product_id.stock_move_ids.state',
    #              'product_id.stock_move_ids.date', 'product_id.stock_move_ids.product_uom_qty')
    @api.depends('product_id','product_id.stock_move_ids', 'product_id.stock_move_ids.state','product_id.stock_move_ids.date', 'product_id.stock_move_ids.product_uom_qty')
    def _compute_forecast_qty(self):
        for rec in self:
            if rec.product_id:
                rec.forecast_quantity =  rec.product_id.product_tmpl_id.incoming_qty
            else:
                rec.forecast_quantity = 0.0



    # Compute Final Safety Stock Level
    @api.depends('max_consumption', 'avg_consumption', 'max_lead_time', 'min_lead_time')
    def _compute_final_safety_stock_level(self):
        for record in self:
            if record.max_consumption and record.max_lead_time:
                record.final_safety_stock_level = (
                    (record.max_consumption / 30.0) * record.max_lead_time
                ) - (
                    (record.avg_consumption / 30.0) * record.min_lead_time
                )
            else:
                record.final_safety_stock_level = 0.0

    # Compute Reorder Level
    @api.depends('avg_consumption', 'avg_lead_time', 'final_safety_stock_level')
    def _compute_reorder_level(self):
        for record in self:
            if record.avg_consumption and record.avg_lead_time:
                record.reorder_level = (
                    (record.avg_consumption / 30.0) * record.avg_lead_time
                ) + record.final_safety_stock_level
            else:
                record.reorder_level = 0.0

    @api.depends('max_lead_time','min_lead_time')
    def _compute_avg_lead_time(self):
        for rec in self:
            if rec.max_lead_time and rec.min_lead_time:
                rec.avg_lead_time = (rec.max_lead_time + rec.min_lead_time) / 2
            else:
                rec.avg_lead_time = 0.0
