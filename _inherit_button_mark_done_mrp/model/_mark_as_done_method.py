from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WriteName(models.Model):
    _inherit = "mrp.production"
    
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="""[
            ('type', 'in', ['product', 'consu']),
            ('level_2_cat', 'in', ['Finished Goods', 'Semi Finished Goods', 'Work In Process']),
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id)
        ]
        """,
        compute='_compute_product_id', store=True, copy=True, precompute=True,
        readonly=True, required=True, check_company=True,
        states={'draft': [('readonly', False)]})
    def button_mark_done(self):
        res=super(WriteName, self).button_mark_done()

        raw_moves = self.mapped('move_raw_ids')
        # raise UserError(str(raw_moves))
        main_product=self.env['stock.move.line'].search([('move_id.product_id','=',self.product_id.id)])
        main_product.write({
            'reference': self.name
        })
        for move in raw_moves:
            valuation_layers = self.env['stock.valuation.layer'].search([('product_id', '=', move.product_id.id)])
            
            for valuation in valuation_layers:
                valuation.write({
                    'reference': self.name
                })
            move_lines = self.env['stock.move.line'].search([('move_id', '=', move.id)])

            for move_line in move_lines:
                move_line.write({
                    'reference': self.name
                })
        return res
