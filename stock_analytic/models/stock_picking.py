# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self = self.with_context(validate_analytic=True)

        res = super().button_validate()

        for rec in self:

            stock_valuation_layers = rec.move_ids.stock_valuation_layer_ids

            if stock_valuation_layers:
                for rec in stock_valuation_layers:
                    stock_move = rec.stock_move_id

                    if not stock_move:
                        continue

                    reference_name = (
                        stock_move.picking_id.name if stock_move.picking_id else 
                        stock_move.production_id.name if stock_move.production_id else 
                        stock_move.raw_material_production_id.name if stock_move.raw_material_production_id else 
                        None
                    )

                    if not reference_name:
                        continue

                    stock_move.write({'reference': reference_name})

                    if rec.account_move_id:
                        ref_value = rec.account_move_id.ref
                        if ref_value and ' ' in ref_value:
                            new_ref_value = ref_value.replace(ref_value.split(' ')[0], reference_name)
                            rec.account_move_id.write({'ref': new_ref_value})

                        rec_description = rec.description
                        if rec_description and ' ' in rec_description:
                            new_description = rec_description.replace(rec_description.split(' ')[0], reference_name)
                            rec.write({'description': new_description})

                        if rec.account_move_id.line_ids:
                            for line in rec.account_move_id.line_ids:
                                line_name = line.name
                                if line_name and ' ' in line_name:
                                    new_line_name = line_name.replace(line_name.split(' ')[0], reference_name)
                                    line.write({'name': new_line_name})



        # raise UserError(['res', res])
