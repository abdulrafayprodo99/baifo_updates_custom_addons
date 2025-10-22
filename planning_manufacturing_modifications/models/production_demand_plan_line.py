from odoo import models,api,fields,_
from odoo.exceptions import UserError, ValidationError

PRODUCTION_DEMAND_PLAN = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
]

class PDOLINE(models.Model):
   _inherit = 'production.demand.plan.line'
   
   scheduled_date = fields.Date(string="Exp. Date of Dispatch")

   @api.depends('shipment_plan','sale_balance_qty','stock_in_hand')
   def compute_demand_qty(self):
      for rec in self:
         rec['demand'] = 0 
         if rec.pdo_id.doc_type == "sale":
               if rec.shipment_plan >= rec.stock_in_hand:
                  stock = rec.shipment_plan - rec.stock_in_hand
                  rec['demand'] = stock
               elif rec.shipment_plan < rec.stock_in_hand:
                  if rec.shipment_plan:
                     raise UserError("Stock is Avaiable, Please Create Delivery Order or Create PDO For Stock ")
         

   @api.constrains('shipment_plan','sale_balance_qty')
   def _check_shipment_plan_not_greater_than_sale_qty(self):  # Aneeq 43,165
      for rec in self:
         sale_balance_qty = rec.sale_balance_qty or 0 
         if rec.shipment_plan > sale_balance_qty:
            raise ValidationError(_("Shipment Plan Quantity (%s) cannot be greater than Sale Order Quantity (%s).") % (rec.shipment_plan, sale_balance_qty))

   
   def update_production_planning(self):
      if self:
         query  =  f"""
            UPDATE affinity_material_demand_lines set product_demand_quantity = {self.demand} WHERE pdo_id = {self._origin.pdo_id.id} AND product_id = {self._origin.product_id.id}; 
         """
         self.env.cr.execute(query)