from odoo import models,api,fields,_
from odoo.exceptions import UserError

class material_requirement_lines(models.Model):  
    _inherit = 'affinity.material.demand.lines'
    
    pdo_id = fields.Many2one("production.demand.plan" , string='PDO ID')
    check_manufacturing_order = fields.Boolean(string='MO Created?' , )
    mo_number = fields.Char("Mo Number")
    mo_qty = fields.Float("Mo Qty", compute="compute_mo_qty")
    remaining_qty = fields.Float("Remaining Qty",compute="compute_remaining_qty")   
    # dispatch_date = fields.Date(string="Exp. Date of Dispatch", compute='_compute_dispatch_date')   #Aneeq 43,165
    production_end_date = fields.Date(string="Production End Date")

    
    # @api.depends('pdo_id', 'product_id')        #Aneeq 43,165
    # def _compute_dispatch_date(self):
    #     for rec in self:
    #         if rec.pdo_id:
    #             dispatch_dates = []
    #             for line in rec.pdo_id.pdo_line_id:
    #                 if line.product_id == rec.product_id and line.scheduled_date:
    #                     dispatch_dates.append(line.scheduled_date)
                
    #             if dispatch_dates:
    #                 rec.dispatch_date = dispatch_dates[0]
    #             else:
    #                 rec.dispatch_date = False
    #         else:
    #             rec.dispatch_date = False
                

    def action_check_and_unlink(self):          #Aneeq 43,165
        for rec in self:
            if rec.remaining_qty == 0:
                rec.unlink()
            else:
                pass
        return True

    def action_view_manufacturing_orders(self):  #Aneeq 43,165
        self.ensure_one()
        domain = [('pdo_id', '=', self.pdo_id.id)]
        return {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': self.env.context,
        }
    
    @api.depends("mo_qty")
    def compute_remaining_qty(self):
        self['remaining_qty'] = 0
        for rec in self:
            rec['remaining_qty'] += rec['product_demand_quantity'] - rec['mo_qty'] 
    
    
    @api.depends('product_id')
    def compute_mo_qty(self):
        for rec in self:
            rec['mo_qty'] = 0
            mrp_production = self.env['mrp.production'].search([('pdo_id','=',rec.pdo_id.id)])
            for mrp in mrp_production:
                if rec.product_id == mrp.product_id:
                    if mrp.state == 'done':
                        rec['mo_qty'] += mrp.product_qty

    def create_manufacturing_order(self):
        list_material_demand = []
        list_bom_components = []
        if self.check_manufacturing_order == False:
            for rec in self:
                search_in_bom = rec.env['mrp.bom'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)])
                if search_in_bom:
                    for bom_lines in search_in_bom.bom_line_ids:
                        list_bom_components.append((0,0,{
                        'product_id' : bom_lines.product_id.id,
                        'product_uom_qty' : bom_lines.product_qty,
                        'product_uom': bom_lines.product_uom_id.id,
                        'bom_line_id' :bom_lines.id,
                        # 'scheduled_date' : date
                    }))

                    mrp_production = self.env['mrp.production']
                    if list_bom_components:
                        mrp = mrp_production.create({
                            'state': 'draft',
                            'product_id' : rec.product_id.id,
                            # 'bom_id' : search_in_bom.product_tmpl_id.id,
                            'product_qty': rec.product_demand_quantity,
                            'x_studio_material_requirement_plan' : rec.material_requirement_id.id,
                            'x_studio_production_demand_plan' : rec.pdo_id.id,
                            'move_raw_ids': list_bom_components
                            }
                        )
                        rec['check_manufacturing_order'] = True
                        rec['mo_number'] = mrp.name
                    else:
                        raise UserError('Nothing To Create')    

                else:
                    raise UserError("Bom Not Found!!!")
        else:
            raise UserError("Manufacturing Order Already Created")
        




    def open_manufacturing_order(self):  #Aneeq 43,165
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Order',
            'res_model': 'mrp.production',  
            'view_mode': 'tree,form', 
            'target': 'current',
            'domain': [
                ('pdo_id', '=', self.pdo_id.id),
                ('product_id', '=', self.product_id.id),
            ],
            'views': [(self.env.ref('mrp.mrp_production_tree_view').id, 'tree')],
            'context': dict(self._context),
        }
