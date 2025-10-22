from odoo import models,api,fields,_
from odoo.exceptions import UserError

PRODUCTION_DEMAND_PLAN = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
]

class PDO(models.Model):
    _inherit="production.demand.plan"

    approval_state = fields.Selection(selection=PRODUCTION_DEMAND_PLAN, string="Approval Status",copy=False,)
class PDOLINE(models.Model):
    _inherit = 'production.demand.plan.line'

    scheduled_date = fields.Date(string="Exp. Date of Dispatch")

class SPDOLINE(models.Model):
    _inherit="stock.production.demand.plan.line"


    scheduled_date = fields.Date(string="Exp. Date of Dispatch")


