# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import re

class MaterialRequirementLine(models.Model):
    _inherit = 'affinity.material.demand.lines'


    process_qty=fields.Float("Process Qty",compute="_compute_mo_process_qty")
    pdo_remarks=fields.Html("Pdo Remarks",compute="_compute_remarks")

    @api.depends("pdo_id")
    def _compute_remarks(self):
        for rec in self:
            rec.pdo_remarks=rec.pdo_id.remarks

    def strip_html_tags(self, html_content):
        clean = re.compile("<.*?>")
        return re.sub(clean, '', html_content)

    def get_pdo_remarks_text(self):
        return self.strip_html_tags(self.pdo_remarks) if self.pdo_remarks else 'N/A'


    def _compute_mo_process_qty(self):
        for rec in self:
            linked_mos=self.env['mrp.production'].search([
                ('product_id','=',rec.product_id.id),
                ('pdo_id','=',rec.pdo_id.id)
                ])
            linked_mos=linked_mos.filtered(lambda mo :  mo.state not in ['done','cancel'])
            rec.process_qty=sum(linked_mos.mapped('product_qty'))




 
    