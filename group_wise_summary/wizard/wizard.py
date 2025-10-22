from odoo import fields, models
from odoo.exceptions import UserError

class SalesSummaryReportWizard(models.TransientModel):
    _name = 'sales.group.summary.report'
    _description = 'Product Group Wise Sales Summary Report'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    
    # product_id = fields.Many2many('product.template', string='Product')
    currency_id = fields.Many2many('res.currency', string='Currency')
    prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise')], string='Product Selection')

    product_id = fields.Many2many(
        'product.template', 
        string='Product',
        domain="[('sale_ok', '=', True), ('categ_id', 'ilike', 'Stock In Trade / Finished Goods')]"
    )

    def _get_product_codes(self):
        products = self.env['product.product'].search([
            ('sale_ok', '=', True),
            ('categ_id', 'ilike', 'Stock In Trade / Finished Goods')  # 'contains' match on category name
        ])
        return [(product.default_code, "{} - {}".format(product.default_code, product.name))
                for product in products if product.default_code]

    product_code_from = fields.Selection(
        selection='_get_product_codes',
        string='Product Code From'
    )

    product_code_to = fields.Selection(
        selection='_get_product_codes',
        string='Product Code To'
    )

    def print_report(self):
        product_ids = []
        if self.product_id:
            product_ids = [product.id for product in self.product_id]
        
        currency_ids = []
        if self.currency_id:
            currency_ids = [currency.id for currency in self.currency_id]

        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_id': product_ids,
            'currency_id': currency_ids,
            'prod_sel': self.prod_sel,
            'product_code_from': self.product_code_from,
            'product_code_to': self.product_code_to,
        }
        return self.env.ref('group_wise_summary.sales_group_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)
