from odoo import models,api,fields,_
from odoo.exceptions import UserError

class SPDOLINE(models.Model):
    _inherit="stock.production.demand.plan.line"


    scheduled_date = fields.Date(string="Exp. Date of Dispatch")
    stock_demand = fields.Float(string='Prd Qty Req./Stock',compute="compute_stock_demand_qty", store=True, readonly=False )

    def update_production_planning(self):
        if not self or not self._origin:
            return

        if not self.stock_demand or not self._origin.stock_pdo_id or not self._origin.product_id:
            return 

        query = f"""
            UPDATE affinity_material_demand_lines 
            SET product_demand_quantity = {self.stock_demand} 
            WHERE pdo_id = {self._origin.stock_pdo_id.id} 
            AND product_id = {self._origin.product_id.id}; 
        """
        self.env.cr.execute(query)

    
            
    @api.onchange('stock_demand')
    def onchange_demand(self):
        self.update_production_planning()


    @api.depends('shipment_plan')
    def compute_stock_demand_qty(self):
        for rec in self:
            rec['stock_demand'] = 0 
            if rec.shipment_plan >= rec.stock_in_hand:
                stock = rec.shipment_plan - rec.stock_in_hand
                rec['stock_demand'] = stock 
            elif rec.shipment_plan < rec.stock_in_hand:
                if rec.shipment_plan:
                    raise UserError("Stock is Avaiable, Please Create Delivery Order or Create PDO For Stock ")


class MRP_Production(models.Model):
    _inherit = "mrp.production"
    
    pdo_id = fields.Many2one(
        'production.demand.plan', 
        'Production Demand Order',
        domain=lambda self: [('id', 'not in', self._get_used_pdo_ids())]
    )
    
    product_category = fields.Char(related="product_id.level_2_cat")
    
        #Update Okasha 24/9/25
    def _get_used_pdo_ids(self):
        demand_lines=self.env['affinity.material.demand.lines'].search([])
        domain=demand_lines.filtered(lambda line : line.remaining_qty==0).mapped('pdo_id.id')
        return domain

        