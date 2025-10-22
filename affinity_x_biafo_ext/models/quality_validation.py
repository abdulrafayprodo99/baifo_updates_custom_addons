from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_quality_check_required = fields.Selection(selection=[('yes','Yes'),('no','No')])


class PurhcaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    _sql_constraints = [
        ('check_quality_point_exists', 
         '''CHECK (
            TRUE
            OR
            NOT EXISTS (
                SELECT 1
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN quality_point_product_rel qppr ON pt.id = qppr.product_tmpl_id
                JOIN quality_point qp ON qppr.quality_point_id = qp.id
                WHERE purchase_request_line.product_id = pp.id
                AND pt.is_quality_check_required = 'yes'
            )
         )''',
         'The product must have an associated quality check when quality check is required.')
    ]

class PurhcaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    _sql_constraints = [
        ('check_quality_point_exists', 
         '''CHECK (
            TRUE
            OR
            NOT EXISTS (
                SELECT 1
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN quality_point_product_rel qppr ON pt.id = qppr.product_tmpl_id
                JOIN quality_point qp ON qppr.quality_point_id = qp.id
                WHERE purchase_order_line.product_id = pp.id
                AND pt.is_quality_check_required = 'yes'
            )
         )''',
         'The product must have an associated quality check when quality check is required.')
    ]

class StockMove(models.Model):
    _inherit = 'stock.move'

    _sql_constraints = [
        ('check_quality_point_exists', 
         '''CHECK (
            TRUE
            OR
            NOT EXISTS (
                SELECT 1
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN quality_point_product_rel qppr ON pt.id = qppr.product_tmpl_id
                JOIN quality_point qp ON qppr.quality_point_id = qp.id
                WHERE stock_move.product_id = pp.id
                AND pt.is_quality_check_required = 'yes'
            )
         )''',
         'The product must have an associated quality check when quality check is required.')
    ]

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    _sql_constraints = [
        ('check_quality_point_exists', 
         '''CHECK (
            TRUE
            OR
            NOT EXISTS (
                SELECT 1
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN quality_point_product_rel qppr ON pt.id = qppr.product_tmpl_id
                JOIN quality_point qp ON qppr.quality_point_id = qp.id
                WHERE mrp_production.product_id = pp.id
                AND pt.is_quality_check_required = 'yes'
            )
         )''',
         'The product must have an associated quality check when quality check is required.')
    ]

