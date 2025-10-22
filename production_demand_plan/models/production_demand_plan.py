from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import json
import datetime
from datetime import datetime, date, timedelta
import calendar



class ProductionDemandPlan(models.Model):
    _name = 'production.demand.plan'
    _description = 'Production Demand Plan'


    name = fields.Char(string='Name' , readonly=True)
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('mr_created','Material Request Created')],string="Status",default="draft")
    approved_state = fields.Selection([('prepared','Prepared'),('verified','Verified'),('verified by coo','Verified By COO')],string="Approve Status")
    sale_order = fields.Many2one("sale.order", string="Sale Order")

    @api.onchange("doc_type")
    def _onchange_sale_order(self):
        sale_orders = self.env["sale.order"].search([
            ("state", "=", "sale"),
            ("order_line", "!=", False),
        ]).filtered(lambda so: any(line.product_uom_qty >line.qty_delivered for line in so.order_line))

        return {
            "domain": {
                "sale_order": [("id", "in", sale_orders.ids)]
            }
        }

    res_partner = fields.Many2one(
    'res.partner', 
    string='Customer ID', 
    domain=[('customer_rank', '>', 0)]
)
    partner_id_domain = fields.Char(string='Supplier Domain',compute="_compute_partner_id_domain", readonly=True, store=False)
    customer_po_no = fields.Char(string='Customer PO No')
    customer_po_date = fields.Date(string='Customer PO Date')
    date = fields.Date(string='Date')
    pdo_line_id = fields.One2many("production.demand.plan.line", 'pdo_id', copy=True ,string="Production Demand Line")
    stock_pdo_line_id = fields.One2many("stock.production.demand.plan.line", 'stock_pdo_id', copy=True ,string="Stock Production Demand Line")
    doc_type = fields.Selection(selection=[('stock','For Stock'),('sale','For Sale')])
    remarks = fields.Char(string='Remarks')    

    @api.model
    def _compute_partner_id_domain(self):
        for record in self:
            record['partner_id_domain'] = False
            customer_ids = []
            partner = self.env['res.partner'].search([])
            for pr in partner:
                if pr.id == self.res_partner.id:
                    if pr.id not in customer_ids:   
                        customer_ids.append(self.res_partner.id)
            record.partner_id_domain = json.dumps([('partner_id', 'in', customer_ids)])
    
    
    
    # @api.multi
    # def create(self):
    #     for rec in self:
    #         rec['name'] = rec.env['ir.sequence'].next_by_code('pdo_seq')
    

    @api.onchange('sale_order')
    def update_product(self):
        for record in self:
            pdo_lines_updates = []
            sno = 1 
            if record.doc_type == 'sale':
                if record.sale_order:
                    sale = self.env['sale.order'].search([('id', '=', record.sale_order.id)])
                    if sale:
                        for pdo_line in record.pdo_line_id:
                            pdo_lines_updates.append((2, pdo_line.id, 0))
                        
                        for so_line in sale.order_line:
                            
                            pdo_lines_updates.append((0, 0, {
                                's_no' : sno,
                                'product_code': so_line.product_id.default_code,
                                'product_id': so_line.product_id.id,
                                'specification': so_line.x_studio_specification,
                                'uom': so_line.product_uom.id,
                                'sale_balance_qty': so_line.product_uom_qty - so_line.qty_delivered,
                                'shipment_plan': 0,
                                'stock_in_hand': so_line.product_id.qty_available,
                                
                            }))
                            sno = sno +1

                        if pdo_lines_updates:
                               record.write({
                        'pdo_line_id': pdo_lines_updates,
                        'res_partner': sale.partner_id.id,
                        'customer_po_no': sale.customer_po_no,
                        'customer_po_date': sale.date_order,
                    })
                            # self['pdo_line_id'] = pdo_lines_updates
                else:
                    for pdo_line in record.pdo_line_id:
                        pdo_line.unlink()
                    
        
    # @api.onchange('sale_order')
    # def get_pdo_line(self):
    #     for rec in self:
    #         # if rec.sale_order:
    #         #     raise UserError("TEST")
    #         # raise UserError("Working")?
           
    #         self['pdo_line_id'] = False
    #         sale_order_line_list_exists = []
    #         sale_order_line_list_not_exists = []
    #         check_list = []
    #         check_list_p = []
    #         check_list_ppp = []
    #         check_list_pppp = []

            

    #         production_order_exists = self.env['production.demand.plan'].search([('sale_order','=',rec.sale_order.id)])
    #         if production_order_exists:
    #             sale_order_id = rec.env['sale.order'].search([('id','=',rec.sale_order.id)])
    #             for sale_line in sale_order_id.order_line:
    #                 check_list.append(str(sale_line.id))
                 
    #             for production_order_exists_line in production_order_exists.pdo_line_id:
    #                 check_list_p.append(int(production_order_exists_line.sale_order_line_id.id))
                
    #             sale_order_id_for_list = self.env['sale.order.line'].search([])
    #             s_no = 0
    #             for sale_line_pp in sale_order_id_for_list:
    #                     s_no = s_no + 1
    #                     if sale_line_pp.order_id.id == rec.sale_order.id:
    #                     # raise UserError(str(sale_line_pp.order_id))?
    #                         if sale_line_pp.id not in check_list_p:
    #                             sale_order_line_list_exists.append((0,0,{
    #                                 's_no' : s_no,
    #                                 'pdo_id' : rec.id,
    #                                 'sale_order_line_id' : sale_line.id,
    #                                 'product_code' : sale_line.product_id.default_code ,
    #                                 'product_id' : sale_line.product_id.id,
    #                                 'specification' : sale_line.x_studio_specification,
    #                                 'uom' : sale_line.product_uom,
    #                                 'sale_balance_qty' : sale_line.product_uom_qty - sale_line.qty_delivered,
    #                                 'shipment_plan': 0,
    #                                 'stock_in_hand': sale_line.product_id.qty_available,
    #                             }))
                        
    #             if sale_order_line_list_exists:
    #                 self['res_partner'] = sale_order_id.partner_id.id
    #                 self['customer_po_no'] = sale_order_id.customer_po_no
    #                 self['customer_po_date'] = sale_order_id.customer_po_date
    #                 self['pdo_line_id'] = sale_order_line_list_exists
    #         else:
    #             sale_order_id_not_exists = self.env['sale.order'].search([('id','=',rec.sale_order.id)])
    #             s_no = 0
    #             for sale_line in sale_order_id_not_exists.order_line:
    #                 s_no = s_no + 1
    #                 sale_order_line_list_not_exists.append((0,0,{
    #                     's_no' : s_no,
    #                     'pdo_id' : rec.id,
    #                     'sale_order_line_id' : sale_line.id,
    #                     'product_code' : sale_line.product_id.default_code ,
    #                     'product_id' : sale_line.product_id.id,
    #                     'specification' : sale_line.x_studio_specification,
    #                     'uom' : sale_line.product_uom,
    #                     'sale_balance_qty' : sale_line.product_uom_qty - sale_line.qty_delivered,
    #                     'shipment_plan': 0,
    #                     'stock_in_hand': sale_line.product_id.qty_available,
    #                     # 'demand' : sale_line.product_uom_qty,
    #                     # 'production_plan_check' : True
    #                 }))
    #             if sale_order_line_list_not_exists:
    #                 self['res_partner'] = sale_order_id_not_exists.partner_id.id
    #                 self['customer_po_no'] = sale_order_id_not_exists.customer_po_no
    #                 self['customer_po_date'] = sale_order_id_not_exists.customer_po_date
    #                 self['pdo_line_id'] = sale_order_line_list_not_exists
                
    
    
                
    def post_action(self):
        self.state = 'approved'
    
    def create_in_material_request(self):
        for rec in self:
            list_pdo = []
            check = False
            if rec.doc_type == 'sale':
                for line in rec.pdo_line_id:
                    if line.scheduled_date and line.product_id.produce_delay:
                        date = False 
                        if not line.urgent_requirment:
                            date = line.scheduled_date - timedelta(days= line.product_id.produce_delay)
                        else:
                            date = line.scheduled_date
                        pdo_weeks = date.isocalendar()[1] - date.replace(day=1).isocalendar()[1] + 1
                        currentdate = date.today()
                        diff = date - currentdate
                        # raise UserError(diff.day)
                        if str(diff) < "0":
                            if line.urgent_requirment != True:
                                raise UserError("Scheduled Date should not be back date")
                    
                    else:
                        raise UserError("Please check Product Scheduled Date or Lead Time")
                    material_req = rec.env['affinity.material.requirement'].search([])
                    for material_requirement in material_req:
                        
                        date_material = material_requirement.date_to
                        mtr_week = date_material.isocalendar()[1] - date_material.replace(day=1).isocalendar()[1] + 1
                        if pdo_weeks == mtr_week:
                            # raise UserError(str(mtr_week) + "---- " + str(pdo_weeks))
                            # list_pdo.append(str(pdo_weeks)+" "+"Week No" +" "+ str(mtr_week) +" "+ str(material_requirement.name))
                            list_pdo.append((0,0,{
                                'pdo_id' : rec.id,
                                'product_id' : line.product_id.id,
                                'product_demand_quantity' : line.demand or line.stock_demand,
                                'customer_id': rec.res_partner.id,
                                'sale_order_id' : rec.sale_order.id,
                                'scheduled_date' : date
                            }))

                            material_requirement['material_demand_line_ids'] = list_pdo
                            rec.state = 'mr_created'
                            
                            list_pdo = []
            elif rec.doc_type == 'stock':
                for line in rec.stock_pdo_line_id:
                    if line.scheduled_date and line.product_id.produce_delay:
                        date = False 
                        if not line.urgent_requirment:
                            date = line.scheduled_date - timedelta(days= line.product_id.produce_delay)
                        else:
                            date = line.scheduled_date
                        pdo_weeks = date.isocalendar()[1] - date.replace(day=1).isocalendar()[1] + 1
                        currentdate = date.today()
                        diff = date - currentdate
                        # raise UserError(diff.day)
                        if str(diff) < "0":
                            if line.urgent_requirment != True:
                                raise UserError("Scheduled Date should not be back date")
                    
                    else:
                        raise UserError("Please check Product Scheduled Date or Lead Time")
                    material_req = rec.env['affinity.material.requirement'].search([])
                    for material_requirement in material_req:
                        
                        date_material = material_requirement.date_to
                        mtr_week = date_material.isocalendar()[1] - date_material.replace(day=1).isocalendar()[1] + 1
                        if pdo_weeks == mtr_week:
                            # raise UserError(str(mtr_week) + "---- " + str(pdo_weeks))
                            # list_pdo.append(str(pdo_weeks)+" "+"Week No" +" "+ str(mtr_week) +" "+ str(material_requirement.name))
                            list_pdo.append((0,0,{
                                'pdo_id' : rec.id,
                                'product_id' : line.product_id.id,
                                'product_demand_quantity' : line.stock_demand,
                                'customer_id': rec.res_partner.id,
                                # 'sale_order_id' : rec.sale_order.id,
                                'scheduled_date' : date
                            }))

                            material_requirement['material_demand_line_ids'] = list_pdo
                            rec.state = 'mr_created'
                            
                            list_pdo = []
                # else:
                # raise UserError("Hello") 
                        
    
    # def create_in_material_request(self):
    #     for rec in self:
    #         # currentdate = date.today()
    #         material_req = rec.env['affinity.material.requirement'].search([])
    #         list_pdo = []
    #         for material_requirement in material_req:
    #             for line in rec.pdo_line_id:
    #                 if line.urgent_requirment:
    #                     # list_pdo.append(str(line.scheduled_date.isocalendar()[1] )+'=='+ str(material_requirement.date_to.isocalendar()[1]))
    #                     if line.scheduled_date.isocalendar()[1] + 1 == material_requirement.date_to.isocalendar()[1] + 1:
    #                         list_pdo.append((0,0,{
    #                             'pdo_id' : rec.id,
    #                             'product_id' : line.product_id.id,
    #                             'product_demand_quantity' : line.demand,
    #                             'customer_id': rec.res_partner.id,
    #                             'sale_order_id' : rec.sale_order.id,
    #                             'scheduled_date' : line.scheduled_date
    #                         }))

    #                         material_requirement['material_demand_line_ids'] = list_pdo
    #                         rec.state = 'mr_created'               
    #                         list_pdo = []
    #                 if not line.urgent_requirment:
    #                     sub_date = line.scheduled_date - timedelta(days= line.product_id.produce_delay)
    #                     if sub_date < date.today():
    #                         raise UserError("Scheduled Date Should be Grater Then Manufacturing Lead time")
    #                     else:
    #                         # raise UserError(str(sub_date.isocalendar()[1]) + "=="+ str(material_requirement.date_to.isocalendar()[1]))
    #                         if sub_date.isocalendar()[1] + 1 == material_requirement.date_to.isocalendar()[1] + 1:
    #                             # raise UserError("Bilal")
    #                             list_pdo.append((0,0,{
    #                                 'pdo_id' : rec.id,
    #                                 'product_id' : line.product_id.id,
    #                                 'product_demand_quantity' : line.demand,
    #                                 'customer_id': rec.res_partner.id,
    #                                 'sale_order_id' : rec.sale_order.id,
    #                                 'scheduled_date' : sub_date
    #                             }))

    #                             material_requirement['material_demand_line_ids'] = list_pdo
    #                             rec.state = 'mr_created'
                                            
    #                             list_pdo = []
    #                     # raise UserError("hello")
                    
   

class material_requirement_lines(models.Model):  
    _inherit = 'affinity.material.demand.lines'
    
    pdo_id = fields.Many2one("production.demand.plan" , string='PDO ID')
    check_manufacturing_order = fields.Boolean(string='MO Created?' , )
    mo_number = fields.Char("Mo Number")
    mo_qty = fields.Float("Mo Qty", compute="compute_mo_qty")
    remaining_qty = fields.Float("Remaining Qty",compute="compute_remaining_qty")
    
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
            



        # raise UserError("Hamza Khan Khattak")
    


class ProductionDemandPlanLine(models.Model):
    _name = 'production.demand.plan.line'
    _description = 'Production Demand Plan Line'

    s_no = fields.Integer(string='S.No')
    
    pdo_id = fields.Many2one("production.demand.plan" , string='PDO ID')
    sale_order_line_id = fields.Many2one("sale.order.line" , string='Sale Order Line ID')
    product_code = fields.Char(string='Product Code')
    product_id = fields.Many2one("product.product" , string='Product')
    uom = fields.Many2one("uom.uom" , string='UOM')
    sale_balance_qty = fields.Float(string='Sale Order Qty')
    shipment_plan =  fields.Float(string='Shipment Plan')
    stock_in_hand = fields.Float(string='Stock In Hand')
    demand = fields.Float(string='Prd Qty Req./Sale' , compute="compute_demand_qty")
    scheduled_date = fields.Date(string='Scheduled Date')
    urgent_requirment = fields.Boolean(string='Urgent Requirment')
    specification = fields.Char(string='Specification')
    # remarks = fields.Char(string='Remarks')
    # stock_demand = fields.Float(string='Prd Qty Req./Stock' )
    
    
    
    doc_type = fields.Selection(selection=[('stock','For Stock'),('sale','For Sale')], compute="compute_doc_type")
    # production_plan_check = fields.Boolean(string='Production Planned')

    @api.depends('pdo_id.doc_type')
    def compute_doc_type(self):
        for rec in self:
            rec['doc_type'] = False
            if rec.pdo_id.doc_type == "stock":
                rec['doc_type'] = "stock"
            elif rec.pdo_id.doc_type == "sale":
                rec['doc_type'] = "sale"
                

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
            
            # raise UserError(abc)
    
    
    
    @api.onchange('product_id')
    def _update_readonly_field_product(self):
        for rec in self:
            if rec.doc_type == "sale":
                raise UserError("You are not allowed to change Product")
            # elif rec.doc_type == "stock":
            #     rec['product_code'] = rec.product_id.default_code
            #     rec['uom'] = rec.product_id.uom_id.id
            #     rec['stock_in_hand'] = rec.product_id.qty_available
            
    @api.onchange('scheduled_date')
    def update_readonly_field_product(self):
        if self.urgent_requirment != True:
            if self.scheduled_date:
                currentdate = date.today()
                diff = self.scheduled_date - currentdate
                if str(diff) < "0":
                
                    raise UserError("Scheduled Date should not be back date")
                
class StockProductionDemandPlanLine(models.Model):
    _name = 'stock.production.demand.plan.line'
    _description = 'Stock Production Demand Plan Line'

    s_no = fields.Integer(string='S.No')
    
    stock_pdo_id = fields.Many2one("production.demand.plan" , string='PDO ID')
    # sale_order_line_id = fields.Many2one("sale.order.line" , string='Sale Order Line ID')
    product_code = fields.Char(string='Product Code')
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("level_2_cat", "=", "Finished Goods")]
    )

    uom = fields.Many2one("uom.uom" , string='UOM')
    # sale_balance_qty = fields.Float(string='Sale Order Qty')
    shipment_plan =  fields.Float(string='Shipment Plan')
    stock_in_hand = fields.Float(string='Stock In Hand')
    # demand = fields.Float(string='Prd Qty Req./Sale' , compute="compute_demand_qty")
    scheduled_date = fields.Date(string='Scheduled Date')
    urgent_requirment = fields.Boolean(string='Urgent Requirment')
    specification = fields.Char(string='Specification')
    # remarks = fields.Char(string='Remarks')
    stock_demand = fields.Float(string='Prd Qty Req./Stock' )
    
    
    doc_type = fields.Selection(selection=[('stock','For Stock'),('sale','For Sale')], compute="compute_doc_type")
    # production_plan_check = fields.Boolean(string='Production Planned')

    @api.depends('stock_pdo_id.doc_type')
    def compute_doc_type(self):
        for rec in self:
            rec['doc_type'] = False
            if rec.stock_pdo_id.doc_type == "stock":
                rec['doc_type'] = "stock"
            elif rec.stock_pdo_id.doc_type == "sale":
                rec['doc_type'] = "sale"
                

    # @api.depends('shipment_plan')
    # def compute_demand_qty(self):
    #     for rec in self:
    #         rec['demand'] = 0 
    #         if rec.pdo_id.doc_type == "sale":
    #             if rec.shipment_plan >= rec.stock_in_hand:
    #                 stock = rec.shipment_plan - rec.stock_in_hand
    #                 rec['demand'] = stock 
    #             elif rec.shipment_plan < rec.stock_in_hand:
    #                 if rec.shipment_plan:
    #                     raise UserError("Stock is Avaiable, Please Create Delivery Order or Create PDO For Stock ")
            
            # raise UserError(abc)
    
    
    
    @api.onchange('product_id')
    def _update_readonly_field_product(self):
        for rec in self:
            # if rec.doc_type == "sale":
            #     raise UserError("You are not allowed to change Product")
            if rec.doc_type == "stock":
                rec['product_code'] = rec.product_id.default_code
                rec['uom'] = rec.product_id.uom_id.id
                rec['stock_in_hand'] = rec.product_id.qty_available
            
    @api.onchange('scheduled_date')
    def update_readonly_field_product(self):
        if self.urgent_requirment != True:
            if self.scheduled_date:
                currentdate = date.today()
                diff = self.scheduled_date - currentdate
                if str(diff) < "0":
                
                    raise UserError("Scheduled Date should not be back date")
                
            
            