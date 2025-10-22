# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
class ProductionDemandPlan(models.Model):
    _inherit = 'production.demand.plan'



    # models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class ProductionDemandPlan(models.Model):
    _inherit = 'production.demand.plan'


    def action_prepared(self):
        for rec in self:
            if rec.pdo_line_id:
                for line in rec.pdo_line_id:
                    if line.demand ==0:
                        raise UserError("Kindly Remove Lines Where Production Qty is 0")
        result = super(ProductionDemandPlan, self).action_prepared()
        return result




