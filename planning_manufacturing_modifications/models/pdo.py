from odoo import models,api,fields,_
from odoo.exceptions import UserError
from datetime import datetime,date as d,timedelta
import traceback

PRODUCTION_DEMAND_PLAN = [
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
   ('canceled','Cancelled')
]

def exception_handler(func):
    def wrapper(self,*args, **kwargs):
        try:
            return func(self,*args, **kwargs)
        except Exception as e:
            error_message = f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}"
            raise UserError(error_message)
    return wrapper

mapping = {'sale': ("pdo_line_id", "demand","pdo_id"),
           'stock': ("stock_pdo_line_id", "stock_demand","stock_pdo_id")
        }
class PDO(models.Model):
    _inherit="production.demand.plan"

    approval_state = fields.Selection(selection=PRODUCTION_DEMAND_PLAN, string="Approval Status",copy=False,)
    remarks =fields.Html("Remarks")


    def get_date(self,line):
        return line.scheduled_date - timedelta(days= line.product_id.produce_delay)
    

    def action_verify(self):
        res=super(PDO,self).action_verify()
        self['verified']=self.env.user.id
        return res

    @exception_handler
    def create_in_material_request(self):
        for rec in self:
            line_ids,qty,pdo = mapping[rec.doc_type]
            pdo_date = d.today()
            for line in getattr(rec,line_ids): 
                if line.scheduled_date and line.product_id.produce_delay:
                    if not line.urgent_requirment:
                        pdo_date = rec.get_date(line)
                    else:
                        pdo_date = line.scheduled_date
                if (pdo_date - d.today()).days < 0 :
                    raise UserError("Scheduled Date should not be back date")
                material_requirement = rec.get_production_planning(pdo_date)
                if material_requirement:
                    material_requirement['material_demand_line_ids'] = [(0,0,{
                        'pdo_id' : rec.id,
                        'product_id' : line.product_id.id,
                        'product_demand_quantity' : getattr(line,qty),
                        'customer_id': rec.res_partner.id,
                        'sale_order_id' : rec.sale_order.id if rec.doc_type == 'sale' else False,
                        'scheduled_date' : pdo_date
                    })]
                    rec.state = 'mr_created'
                else:
                    raise UserError("Please check Product Scheduled Date or Lead Time")

    def get_production_planning(self,pdo_date,**kwargs):
        self.ensure_one()
        production_pl = self.env['affinity.material.requirement'].search([('date_from', '<=', pdo_date),('date_to', '>=', pdo_date)],limit=1)
        if kwargs.get('product_id') and kwargs.get('pdo_id'):
            production_pl = production_pl.material_demand_line_ids.filtered(lambda x: x.product_id.id == kwargs.get('product_id') and x.pdo_id.id == kwargs.get('pdo_id'))
        return production_pl

    
    # def action_revise(self):
    #     raise UserError(_("This action is not allowed. Please contact your system administrator."))
    #     for rec in self:
    #         line_ids,qty,pdo = mapping[rec.doc_type]
    #         pdo+=".id"
    #         for line in getattr(rec,line_ids):
    #             if  rec.env['mrp.production'].search([('pdo_id','=',rec.get_nested_attr(line,pdo))]):
    #                 query = f"""
    #                     UPDATE  affinity_material_demand_lines set product_demand_quantity = {getattr(line,qty)} WHERE pdo_id = {rec.get_nested_attr(line,pdo)} AND product_id = {line.product_id.id}; 
    #                 """
    #                 rec.env.cr.execute(query)
    #             else:
    #                 query = f"""
    #                     DELETE FROM affinity_material_demand_lines WHERE pdo_id = {self.get_nested_attr(line,pdo)} AND product_id = {line.product_id.id}; 
    #                 """
    #                 rec.env.cr.execute(query)
    #                 rec.state = False




    def action_revise(self):
        for rec in self:

            line_ids, qty, pdo = mapping[rec.doc_type]
            pdo += ".id"
            for line in getattr(rec, line_ids):
                pdo_val = rec.get_nested_attr(line, pdo)
                if rec.env['mrp.production'].search([('pdo_id', '=', pdo_val)]):
                    query = f"""
                        UPDATE affinity_material_demand_lines
                        SET product_demand_quantity = {getattr(line, qty)}
                        WHERE pdo_id = {pdo_val} AND product_id = {line.product_id.id};
                    """
                    rec.env.cr.execute(query)
                else:
                    query = f"""
                        DELETE FROM affinity_material_demand_lines
                        WHERE pdo_id = {pdo_val} AND product_id = {line.product_id.id};
                    """
                    rec.env.cr.execute(query)
                    rec.state = False

            # Optional: Add UI popup notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Material demand lines revised successfully.'),
                    'type': 'success',
                    'sticky': False,
                }
            }


    def action_cancel(self):
        for rec in self:
            if  rec.approval_state == 'approve':    
                rec.remove_lines_from_production_planning()
                rec.approval_state = 'canceled'
            
    def get_nested_attr(self,obj, attr_path):
        attrs = attr_path.split(".")  
        for attr in attrs:
            obj = getattr(obj, attr)
        return obj
    def remove_lines_from_production_planning(self):
        self.ensure_one()
        line_ids,qty,pdo = mapping[self.doc_type]
        pdo+=".id"
        for line in getattr(self,line_ids):
            query = f"""
                DELETE FROM affinity_material_demand_lines WHERE pdo_id = {self.get_nested_attr(line,pdo)} AND product_id = {line.product_id.id}; 
            """
            self.env.cr.execute(query)
         

    def update_sale_balance_qty(self):     #Aneeq 43,165
        for rec in self:
            for pdo_line, so_line in zip(rec.pdo_line_id, rec.sale_order.order_line):
                qty = so_line.product_uom_qty  
                delivered = so_line.qty_delivered  
                sale_balance_qty = pdo_line.sale_balance_qty  
                
                sale_balance_qty = qty - delivered
                
                pdo_line.sale_balance_qty = sale_balance_qty