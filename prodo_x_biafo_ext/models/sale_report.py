# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import UserError

class SaleReportInherit(models.Model):
    _inherit = "sale.report"

    
    tag_name =  fields.Char('Tag', readonly=True)


    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['tag_name'] = "tag_rpc.name ->>'en_US'"
        return res
    

    
    
    def _from_sale(self):
        from_ = super(SaleReportInherit, self)._from_sale()
        from_ += """LEFT JOIN res_partner_res_partner_category_rel tags ON (tags.partner_id = partner.id)
                LEFT JOIN res_partner_category tag_rpc ON tag_rpc.id = tags.category_id
            """
        return from_

    def _group_by_sale(self):
        group_by_ = super(SaleReportInherit, self)._group_by_sale()
        group_by_ += ", tag_rpc.name ->>'en_US'"
        return group_by_

    
    def _query(self):
        with_ = self._with_sale()
        
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select_sale()}
            FROM {self._from_sale()}
            WHERE {self._where_sale()}
            GROUP BY {self._group_by_sale()}
            {")" if with_ else ""}
        """
