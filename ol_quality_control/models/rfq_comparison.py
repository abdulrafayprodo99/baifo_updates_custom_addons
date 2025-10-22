from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime
import json
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class RfqComparisonVendorSelection(models.Model):
    _inherit = 'rfq.comparison.vendor.selection'

    product_uom_id=fields.Many2one('uom.uom','UoM',compute="_compute_uom_id")

    @api.depends("product_id")
    def _compute_uom_id(self):
        for rec in self:
            rec.product_uom_id= rec.product_id.uom_id.id

class RfqComparison(models.Model):
    _inherit = 'rfq.comparison'

    def generate_rfqs(self):
        for record in self:
            if record.po_approval_state == "approve_ceo":
                valid_comparison = True
                if record.vendor_selection_ids:
                    for line in record.vendor_selection_ids:
                        if not line.partner_id:
                            valid_comparison = False
                else:
                    valid_comparison = False
                
                if not valid_comparison:
                    raise UserError('Please fill the vendor selection details')
                else:
                    #generate rfq
                    vendor_ids = []
                    for line in record.vendor_selection_ids:
                        if line.partner_id.id not in vendor_ids:
                            vendor_ids.append(line.partner_id.id)

                    if vendor_ids:
                        for vendor_id in vendor_ids:
                            po_line_data = []
                            rfq_name = ''
                            vendor_line_ids = record.vendor_selection_ids.filtered(lambda vendor_line_id: vendor_line_id.partner_id.id == vendor_id)
                            po_line_ids = record.po_detail_ids.filtered(lambda po_line_id: po_line_id.partner_id.id == vendor_id)
                            if po_line_ids:
                                for po_line in po_line_ids:
                                    rfq_name = po_line.purchase_order_id.name
                                   
                                    break

                            pterm_id = 0
                            for vendor_line in vendor_line_ids:
                                pterm_id = vendor_line.payment_term_id.id if vendor_line.payment_term_id else 0
                                break

                            if vendor_line_ids:
                                for vendor_line in vendor_line_ids:
                                    po_line_data.append((0,0,{
                                        'product_id':vendor_line.product_id.id,
                                        'account_id':vendor_line.account_id.id,
                                        'specification':vendor_line.specifications,
                                        'product_specification': vendor_line.product_id.product_tmpl_id.product_specification,
                                        'date_planned': datetime.now(),
                                        'product_qty':vendor_line.product_qty,
                                        'product_uom':vendor_line.product_uom_id.id,
                                        'price_unit':vendor_line.product_unit_price,
                                        'taxes_id':vendor_line.tax_ids.ids,
                                    }))
                                # Noman
                                order_ids = []
                                picking_type_ids = []
                                delivery_address = []
                                detail = []
                                for vendor_li in vendor_line_ids:
                                    purchase = self.env['purchase.order'].search([('purchase_request_id','=',record.purchase_request_id.id),('partner_id','=',vendor_li.partner_id.id)])
                                    for pur in purchase:
                                        if pur:
                                            order_ids.append(pur.currency_id.id)
                                            picking_type_ids.append(pur.picking_type_id.id)
                                            delivery_address.append(pur.x_studio_delivery_address.id)
                                            
                                            detail.append({
                                                "country_origin": pur.country_origin.id,
                                                "incoterm_id": pur.incoterm_id.id,
                                                "incoterm_location":pur.incoterm_location,
                                                "port_location":pur.port_location.id
                                            })            
                                
                                # Noman
                                created_po = self.env['purchase.order'].create({
                                    'state': 'to approve',
                                    'partner_id': vendor_id, 
                                    'date_planned': datetime.now(),
                                    'purchase_request_id': record.purchase_request_id.id if record.purchase_request_id else False,
                                    'pr_type': record.purchase_request_id.pr_type if record.purchase_request_id.pr_type else False,
                                    'opex_type': record.purchase_request_id.opex_type if record.purchase_request_id.opex_type else False,
                                    'opex_sub_type': record.purchase_request_id.opex_sub_type if record.purchase_request_id.opex_sub_type else False,
                                    'capex_type': record.purchase_request_id.capex_type if record.purchase_request_id.capex_type else False,
                                    'order_line': po_line_data, 
                                    'rfq_sequence': rfq_name, 
                                    'currency_id': order_ids[0] if order_ids else False, 
                                    'x_studio_delivery_address' : delivery_address[0] if delivery_address else False,
                                    'picking_type_id': picking_type_ids[0] if picking_type_ids else False, 
                                    'payment_term_id': pterm_id if pterm_id != 0 else False, 
                                    
                                    "country_origin": detail[0]['country_origin'] if detail else False,
                                    "incoterm_id": detail[0]['incoterm_id'] if detail else False,
                                    "incoterm_location":detail[0]['incoterm_location'] if detail else False,
                                    "port_location":detail[0]['port_location'] if detail else False,
                                })
                                # raise UserError("hello")
                                if created_po:
                                    for field_name, field in created_po._fields.items():
                                        #raise UserError(str(field_name))
                                        field.readonly = True
                                    # bilal start
                                    for po_line in record.po_detail_ids:
                                        po_line.purchase_order_id.state = "comparative done"
                                        # po_line.purchase_order_id.button_done()
                                    # bilal end
                    #update the status
                    record.write({
                        'state': 'done',
                    })

            else:
                raise UserError("Approval Required")






    