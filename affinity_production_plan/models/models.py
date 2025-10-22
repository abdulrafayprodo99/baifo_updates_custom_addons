# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError
    

class affinity_material_requirement(models.Model):
    _name = 'affinity.material.requirement'

    name = fields.Char(required=True)
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    material_requirement_line_ids = fields.One2many(comodel_name='affinity.material.requirement.lines',inverse_name= 'material_requirement_id', rel='req_req_lines', string='Material Requirement Lines', index=True)
    material_demand_line_ids = fields.One2many(comodel_name= 'affinity.material.demand.lines', inverse_name='material_requirement_id', rel='req_demand_lines', string='Material Requirement Lines', index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def remove_semi_finished_goods_from_planning(self):
        for record in self:
            if record.material_requirement_line_ids:
                for line in record.material_requirement_line_ids:
                    if 'Raw Material' not in line.product_category_id.complete_name:
                        line.unlink()


    def validate_request_line_planning(self):
        for record in self:
            filtered_requirement_lines = record.material_requirement_line_ids.filtered(lambda mr_line: not mr_line.checked_bom)
            if filtered_requirement_lines:
                for line in filtered_requirement_lines:
                    record._get_req_line_bom_components(line.product_id, line.product_required_qty, line.demand_line_ids, line)
                    line.write({
                        'checked_bom':True,
                    })
            filtered_requirement_lines = record.material_requirement_line_ids.filtered(lambda mr_line: not mr_line.checked_bom)
            if filtered_requirement_lines:
                record.validate_request_line_planning()
            # else:
            #     record.remove_semi_finished_goods_from_planning()

    def validate_planning(self):
        for record in self:
            if record.material_demand_line_ids:
                for demand_line in record.material_demand_line_ids:
                    demand_line._get_bom_components(demand_line.id)
                record.validate_request_line_planning()
                record.write({
                    'state':'validated',
                })

    def set_planning_to_draft(self):
        for record in self:
            for line in record.material_requirement_line_ids:
                line.unlink()
            record.write({
                'state':'draft',
            })

    def _get_req_line_bom_components(self,product_id, total_qty_required, demand_line_ids, request_line):
        for record in self:
            product_bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_id.product_tmpl_id.id)])
            if product_bom:
                for bom in product_bom:
                    for line in bom.bom_line_ids:
                        record._upsert_req_bom_component_to_line(line.product_id,line.product_uom_id,line.product_qty,total_qty_required,demand_line_ids,request_line)
    
    def _upsert_req_bom_component_to_line(self, product_id, product_uom_id, product_qty, total_qty_required, demand_line_ids, request_line):
        for record in self:
            product_quantity = product_qty * total_qty_required
            requirement_filtered_lines = record.material_requirement_line_ids.filtered(lambda req_line: req_line.product_id.id == product_id.id)
            if requirement_filtered_lines:
                for line in requirement_filtered_lines:
                    product_quantity += line.product_required_qty
                    #convert demand line ids to list and remove last element
                    demand_line_ids_lst = line.demand_line_ids.split(',')
                    demand_line_ids_lst.pop()
                    args_demand_line_ids_lst = demand_line_ids.split(',')
                    args_demand_line_ids_lst.pop()
                    for item in args_demand_line_ids_lst:
                        if item in demand_line_ids_lst:
                            args_demand_line_ids_lst.remove(item)
                    demand_line_ids_lst.extend(args_demand_line_ids_lst)
                    demand_line_ids_str = ''
                    for item in demand_line_ids_lst:
                        demand_line_ids_str += str(item)+','
                    line.write({
                        'product_required_qty': product_quantity,
                        'demand_line_ids': demand_line_ids_str,
                    })
                return
            
            supplier_id = False
            # product_quantity = product_qty * total_qty_required
            product_on_hand_stock = 0
            wip_product_qty_in_stock = 0
            for line in product_id.seller_ids:
                supplier_id = line.partner_id
                break
            
            #check assembled qty
            assembled_product_qty_in_stock = 0
            bom_line_ids = self.env['mrp.bom.line'].search([('product_id','=',product_id.id)])
            bom_ids = []
            bom_id_mapped_qty = {}
            if bom_line_ids:
                for line in bom_line_ids:
                    bom_ids.append(line.bom_id)
                    bom_id_mapped_qty.update({
                        line.bom_id.id: line.product_qty
                    })
            
            assembled_products = []
            assembled_products_mapped_qty = {}
            if bom_ids:
                for bom_id in bom_ids:
                    assembled_products.append(bom_id.product_tmpl_id)
                    assembled_products_mapped_qty.update({
                        bom_id.product_tmpl_id.id: bom_id_mapped_qty.get(bom_id.id)
                    })
            
            #check assembled qty in stock
            if assembled_products:
                for assembled_product in assembled_products:
                    stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_tmpl_id','=',assembled_product.id)])
                    if stock_quants:
                        for quant in stock_quants:
                            assembled_product_qty_in_stock += (quant.available_quantity * assembled_products_mapped_qty.get(assembled_product.id))

            stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_id','=',product_id.id),('location_id.storage_location','=',False)])
            if stock_quants:
                for quant in stock_quants:
                    product_on_hand_stock += quant.available_quantity
            
            #wip product qty
            stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_id','=',product_id.id),('location_id.storage_location','!=',False)])
            if stock_quants:
                for quant in stock_quants:
                    wip_product_qty_in_stock += quant.available_quantity

            #calculate assembled qty
            nested_assembled_qty = 0
            if request_line.product_required_qty != 0:
                nested_assembled_qty = product_quantity / request_line.product_required_qty
                nested_assembled_qty = request_line.product_assembled_qty * nested_assembled_qty
            new_req_line = self.env['affinity.material.requirement.lines'].create({
                'material_requirement_id':record.id,
                'product_id':product_id.id,
                'product_category_id':product_id.categ_id.id,
                'product_uom_id':product_uom_id.id,
                'supplier_id': supplier_id.id if supplier_id else False,
                'product_assembled_qty': assembled_product_qty_in_stock + nested_assembled_qty,
                'product_qty' : product_on_hand_stock,
                'product_qty_wip' : wip_product_qty_in_stock,
                'product_required_qty': product_quantity,
                'checked_bom':False,
                'demand_line_ids': str(demand_line_ids),
            })


            

class affinity_material_demand_lines(models.Model):
    _name = 'affinity.material.demand.lines'

    material_requirement_id = fields.Many2one('affinity.material.requirement', rel='demand_lines_req', string='Material Req', index=True)
    product_id = fields.Many2one('product.product', string='Product (Finished Good)', index=True)
    product_demand_quantity = fields.Float(string='Demand Quantity')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    customer_id = fields.Many2one('res.partner', string='Customer')
    scheduled_date = fields.Date('Scheduled Date')
    # check_manufacturing_order = fields.Boolean(string='MO Created?' , )
    # mo_number = fields.Char("Mo Number")
    
   
                

    
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        for record in self:
            if record.sale_order_id:
                record.customer_id = record.sale_order_id.partner_id.id if record.sale_order_id.partner_id else False

    def _get_bom_components(self, demand_line_id):
        for record in self:
            product_bom = self.env['mrp.bom'].search([('product_tmpl_id','=',record.product_id.product_tmpl_id.id)])
            if product_bom:
                for bom in product_bom:
                    for line in bom.bom_line_ids:
                        record._upsert_bom_component_to_line(line.product_id,line.product_uom_id,line.product_qty,demand_line_id)

    def _upsert_bom_component_to_line(self, product_id, product_uom_id, product_qty, demand_line_id):
        for record in self:
            product_quantity = product_qty * record.product_demand_quantity
            requirement_filtered_lines = record.material_requirement_id.material_requirement_line_ids.filtered(lambda req_line: req_line.product_id.id == product_id.id)
            if requirement_filtered_lines:
                for line in requirement_filtered_lines:
                    product_quantity_cummulative = product_quantity + line.product_required_qty
                    demand_line_ids_str = line.demand_line_ids
                    demand_line_ids_str += str(demand_line_id)+','
                    line.write({
                        'product_required_qty': product_quantity_cummulative,
                        'demand_line_ids': demand_line_ids_str,
                    })
                return

            supplier_id = False
            product_on_hand_stock = 0
            wip_product_qty_in_stock = 0
            for line in product_id.seller_ids:
                supplier_id = line.partner_id
                break
            
            #check assembled qty
            assembled_product_qty_in_stock = 0
            bom_line_ids = self.env['mrp.bom.line'].search([('product_id','=',product_id.id)])
            bom_ids = []
            bom_id_mapped_qty = {}
            if bom_line_ids:
                for line in bom_line_ids:
                    bom_ids.append(line.bom_id)
                    bom_id_mapped_qty.update({
                        line.bom_id.id: line.product_qty
                    })
            
            assembled_products = []
            assembled_products_mapped_qty = {}
            if bom_ids:
                for bom_id in bom_ids:
                    assembled_products.append(bom_id.product_tmpl_id)
                    assembled_products_mapped_qty.update({
                        bom_id.product_tmpl_id.id: bom_id_mapped_qty.get(bom_id.id)
                    })
            
            #check assembled qty in stock
            if assembled_products:
                for assembled_product in assembled_products:
                    stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_tmpl_id','=',assembled_product.id)])
                    if stock_quants:
                        for quant in stock_quants:
                            assembled_product_qty_in_stock += (quant.available_quantity * assembled_products_mapped_qty.get(assembled_product.id))

            stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_id','=',product_id.id),('location_id.storage_location','=',False)])
            if stock_quants:
                for quant in stock_quants:
                    product_on_hand_stock += quant.available_quantity

            #wip product qty
            stock_quants = self.env['stock.quant'].search([('location_id.usage','=','internal'),('product_id','=',product_id.id),('location_id.storage_location','!=',False)])
            if stock_quants:
                for quant in stock_quants:
                    wip_product_qty_in_stock += quant.available_quantity

            demand_qty = product_quantity - (product_on_hand_stock + wip_product_qty_in_stock + assembled_product_qty_in_stock)
            
            self.env['affinity.material.requirement.lines'].create({
                'material_requirement_id':record.material_requirement_id.id,
                'product_id':product_id.id,
                'product_category_id':product_id.categ_id.id,
                'product_uom_id':product_uom_id.id,
                'supplier_id': supplier_id.id if supplier_id else False,
                'product_assembled_qty': assembled_product_qty_in_stock,
                'product_qty' : product_on_hand_stock,
                'product_qty_wip' : wip_product_qty_in_stock,
                'product_required_qty': product_quantity,
                'checked_bom':False,
                'demand_line_ids':str(demand_line_id)+',',
            })


    def create_manufacturing_order(self):
        for rec in self:
            raise UserError("Khattak")

class affinity_material_requirement_lines(models.Model):
    _name = 'affinity.material.requirement.lines'

    material_requirement_id = fields.Many2one('affinity.material.requirement', rel='req_lines_req', string='Material Req', index=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, index=True)
    product_category_id = fields.Many2one('product.category', string='Product Category', readonly=True, index=True)
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', readonly=True, index=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier',readonly=True, index=True)
    product_assembled_qty = fields.Float(string='Qty in Assembled Units', readonly=True)
    product_qty_wip = fields.Float(string='WIP', readonly=True)
    product_qty = fields.Float(string='Warehouse', readonly=True)
    product_required_qty = fields.Float(string='Required Qty', readonly=True)
    total_qty_required = fields.Float(string='Net Qty Required', store=False, compute='_compute_total_qty_required', readonly=True)
    actual_demand_qty = fields.Float(string='Actual Demand Qty')
    checked_bom = fields.Boolean(default=False)
    demand_line_ids = fields.Char(string="Material Demand Ids", readonly=True)

    @api.depends('product_assembled_qty','product_qty','product_qty_wip','product_required_qty')
    def _compute_total_qty_required(self):
        for record in self:
            total_qty_required = (record.product_assembled_qty + record.product_qty + record.product_qty_wip)-(record.product_required_qty)
            if total_qty_required < 0:
                record.actual_demand_qty = total_qty_required*-1
                record.total_qty_required = total_qty_required*-1
            else:
                record.actual_demand_qty = 0
                record.total_qty_required = 0

    def _commpute_details_of_product(self):
        for record in self:
            if record.product_id:
               record.product_uom_id = record.product_id.uom_po_id.id
               record.product_category_id = record.product_id.categ_id.id
               for vendor_id in record.product_id.seller_ids:
                    record.supplier_id = vendor_id.id
                    break



class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    storage_location = fields.Selection([
        ('wip', 'Work in Progress')
    ], string='Storage Location')
        

    
