from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class GroupedLots(models.Model):
    _inherit = "stock.picking"

    def group_move_lines(self,move_lines):
        grouped_lines = {}

        for line in self.move_line_ids_without_package:
            key = str(line.product_id.id)

            if key not in grouped_lines:
                grouped_lines[key] = {
                    'product_name': line.product_id.name,
                    'p_class': line.product_id.product_tmpl_id.class_,
                    'division': line.product_id.product_tmpl_id.division,
                    'quantity': line.qty_done,
                    'package_count': line.no_of_ctn,
                    'lot_ids': [line.lot_id.name] if line.lot_id else [],
                }
            else:
                grouped_lines[key]['quantity'] += line.qty_done
                grouped_lines[key]['package_count'] += line.no_of_ctn or 0

                # grouped_lines[key]['package_count'] += line.no_of_ctn  # Uncomment if needed
                if line.lot_id and line.lot_id.name not in grouped_lines[key]['lot_ids']:
                    grouped_lines[key]['lot_ids'].append(line.lot_id.name)
        return grouped_lines.values()



