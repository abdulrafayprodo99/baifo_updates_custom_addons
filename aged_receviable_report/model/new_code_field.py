from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from itertools import chain
from dateutil.relativedelta import relativedelta
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import logging
import ast
import datetime
import io
import json
import logging
import math
import re
import base64
from ast import literal_eval
from collections import defaultdict
from functools import cmp_to_key

import markupsafe
from babel.dates import get_quarter_names
from dateutil.relativedelta import relativedelta

from odoo.addons.web.controllers.utils import clean_action
from odoo import models, fields, api, _, osv, _lt
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
from odoo.tools.float_utils import float_round
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from odoo.tools.safe_eval import expr_eval, safe_eval
from odoo.models import check_method_name
_logger = logging.getLogger(__name__)


class Inherit_account_move_line(models.Model):
    _inherit="res.partner"

    
    new_code = fields.Char(
        string='New Code',
    )

    # @api.depends('purchase_line_ids')
    # def _compute_on_time_rate(self):
    #     # order_lines = self.env['purchase.order.line'].search([
    #     #     ('partner_id', 'in', self.ids),
    #     #     ('date_order', '>', fields.Date.today() - timedelta(365)),
    #     #     ('qty_received', '!=', 0),
    #     # ]).filtered(lambda l: l.product_id.sudo().product_tmpl_id.type != 'service' and l.order_id.state in ['done', 'purchase'])
    #     # partner_dict = {}
    #     # for line in order_lines:
    #     #     on_time, ordered = partner_dict.get(line.partner_id, (0, 0))
    #     #     ordered += line.product_uom_qty
    #     #     on_time += sum(line.mapped('move_ids').filtered(lambda m: m.state == 'done' and m.date.date() <= m.purchase_line_id.date_planned.date()).mapped('quantity_done'))
    #     #     partner_dict[line.partner_id] = (on_time, ordered)
    #     # seen_partner = self.env['res.partner']
    #     # for partner, numbers in partner_dict.items():
    #     #     seen_partner |= partner
    #     #     on_time, ordered = numbers
    #     #     partner.on_time_rate = on_time / ordered * 100 if ordered else -1   # use negative number to indicate no data
    #     # (self - seen_partner).on_time_rate = -1
    #     # Ensure partner IDs are in tuple format
    #     partner_ids = tuple(self.ids) if len(self.ids) > 1 else (self.ids[0],)
    
    #     query = """
    #         SELECT pol.partner_id, SUM(pol.product_uom_qty) AS ordered, SUM(sm.product_uom_qty) AS on_time
    #         FROM purchase_order_line pol
    #         LEFT JOIN purchase_order po ON po.id = pol.order_id
    #         LEFT JOIN stock_move sm ON sm.purchase_line_id = pol.id
    #         WHERE pol.partner_id IN %s
    #         AND po.date_order > %s
    #         AND pol.qty_received != 0
    #         AND po.state IN ('done', 'purchase')
    #         AND sm.state = 'done'
    #         AND sm.date <= pol.date_planned
    #         GROUP BY pol.partner_id
    #     """
        
    #     # Execute query with correctly formatted partner_ids and date filter
    #     self.env.cr.execute(query, [partner_ids, fields.Date.today() - timedelta(365)])
    #     result = self.env.cr.fetchall()

    #     partner_dict = {row[0]: (row[2] or 0, row[1] or 0) for row in result}
    #     seen_partner = self.env['res.partner']
    #     for partner in self:
    #         if partner.id in partner_dict:
    #             on_time, ordered = partner_dict[partner.id]
    #             partner.on_time_rate = on_time / ordered * 100 if ordered else -1
    #             seen_partner |= partner
    #         else:
    #             partner.on_time_rate = -1
    #     (self - seen_partner).on_time_rate = -1