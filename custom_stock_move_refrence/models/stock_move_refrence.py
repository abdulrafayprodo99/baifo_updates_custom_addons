from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            if picking.move_ids:
                picking.move_ids.write({'reference': picking.name}) 
                for move in picking.move_ids:
                    if move.move_line_ids:
                        move.move_line_ids.write({'reference': picking.name}) 
        return res



class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for rec in self:
            if rec.move_raw_ids:
                rec.move_raw_ids.write({'reference': rec.name})
                rec.move_raw_ids.mapped('move_line_ids').write({'reference': rec.name})
            if rec.move_finished_ids:
                rec.move_finished_ids.write({'reference': rec.name})
                rec.move_finished_ids.mapped('move_line_ids').write({'reference': rec.name})
        return res

