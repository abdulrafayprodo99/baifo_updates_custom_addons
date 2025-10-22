from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.model
    def create_return_stock_sequence(self,sequence_code):
        sequence_obj = self.env['ir.sequence']
        return_sequence = sequence_obj.next_by_code(sequence_code)  
        return return_sequence 
    @api.constrains('state')
    def name_aloting(self):
        for picking in self:
            if picking.state =='done':
                if picking.origin:
                    if "Return" in picking.origin and "GRN" in picking.origin:
                        if picking.picking_type_id.id ==20:
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.import')
                        if picking.picking_type_id.id ==66:
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.local')
                        if picking.picking_type_id.id  ==21:
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.consumable')
                        if picking.picking_type_id.id  ==17:
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.consumable.hf')
                        if picking.picking_type_id.id  ==67:
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.fixed.asset')
                    elif "Return" in picking.origin and ("DOL" in picking.origin or "DOE" in picking.origin):
                            picking.name=picking.create_return_stock_sequence('stock.return.sequence.customer')