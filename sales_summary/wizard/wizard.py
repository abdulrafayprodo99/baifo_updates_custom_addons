# # # # from odoo import fields, models
# # # # from odoo.exceptions import UserError

# # # # class SalesSummaryReportWizard(models.TransientModel):
# # # #     _name = 'sales.summary.report'
# # # #     _description = 'Sales Summary Report'

# # # #     date_from = fields.Date(string='Start Date')
# # # #     date_to = fields.Date(string='End Date')
# # # #     cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('all customers', 'All Customers')], string='Customer Selection')
# # # #     prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
# # # #     category_id = fields.Many2many('product.category', string='Product Categories')
# # # #     customer_id = fields.Many2many('res.partner', string='Customer')
# # # #     product_id = fields.Many2many('product.template', string='Product')
# # # #     currency_id = fields.Many2many('res.currency', string = 'Currency')
# # # #     product_code_from = fields.Char(string='Product Code From')
# # # #     product_code_to = fields.Char(string='Product Code To')
# # # #     # invocie_type = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Canecelled')], string='Invoice Type')

# # # #     def print_report(self):
# # # #         # Validation
# # # #         if self.cust_sel == 'customer wise' and not self.customer_id:
# # # #             raise UserError("Please select a customer.")
# # # #         if self.prod_sel == 'product wise' and not self.product_id:
# # # #             raise UserError("Please select a product.")
# # # #         if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
# # # #             raise UserError("Please enter both Product Code From and Product Code To.")
# # # #         if self.prod_sel == 'category wise' and not self.category_id:
# # # #             raise UserError("Please select a product category.")
        
# # # #         category_id = []
# # # #         if self.category_id:
# # # #             for id in self.category_id:
# # # #                 category_id.append(id.id)

# # # #         customer_id = []
# # # #         if self.customer_id:
# # # #             for id in self.customer_id:
# # # #                 customer_id.append(id.id)

# # # #         product_id = []
# # # #         if self.product_id:
# # # #             for id in self.product_id:
# # # #                 product_id.append(id.id)
        
# # # #         currency_id = []
# # # #         if self.currency_id:
# # # #             for id in self.currency_id:
# # # #                 currency_id.append(id.id)

# # # #         data = {
# # # #             'date_from': self.date_from,
# # # #             'date_to': self.date_to,
# # # #             'cust_sel': self.cust_sel,
# # # #             'prod_sel': self.prod_sel,
# # # #             'category_id': category_id,
# # # #             'customer_id': customer_id,
# # # #             'currency_id': currency_id,
# # # #             'product_id': product_id,
# # # #             'product_code_from': self.product_code_from,
# # # #             'product_code_to': self.product_code_to,
# # # #             # 'invoice_type': self.invocie_type,
            
# # # #         }
# # # #         return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)







# # # # from odoo import fields, models
# # # # from odoo.exceptions import UserError

# # # # class SalesSummaryReportWizard(models.TransientModel):
# # # #     _name = 'sales.summary.report'
# # # #     _description = 'Sales Summary Report'

# # # #     date_from = fields.Date(string='Start Date')
# # # #     date_to = fields.Date(string='End Date')
# # # #     cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('all customers', 'All Customers')], string='Customer Selection')
# # # #     prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
# # # #     category_id = fields.Many2many('product.category', string='Product Categories')
# # # #     customer_id = fields.Many2many('res.partner', string='Customer')
# # # #     product_id = fields.Many2many('product.template', string='Product')
# # # #     currency_id = fields.Many2many('res.currency', string = 'Currency')

# # # #     def _get_product_codes(self):
# # # #         products = self.env['product.product'].search([])
# # # #         unique_codes = set(product.default_code for product in products if product.default_code)
# # # #         return [(code, code) for code in sorted(unique_codes)]

# # # #     product_code_from = fields.Selection(
# # # #         selection='_get_product_codes',
# # # #         string='Product Code From'
# # # #     )

# # # #     product_code_to = fields.Selection(
# # # #         selection='_get_product_codes',
# # # #         string='Product Code To'
# # # # )


# # # #     # invocie_type = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Canecelled')], string='Invoice Type')

# # # #     def print_report(self):
# # # #         # Validation
# # # #         if self.cust_sel == 'customer wise' and not self.customer_id:
# # # #             raise UserError("Please select a customer.")
# # # #         if self.prod_sel == 'product wise' and not self.product_id:
# # # #             raise UserError("Please select a product.")
# # # #         if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
# # # #             raise UserError("Please enter both Product Code From and Product Code To.")
# # # #         if self.prod_sel == 'category wise' and not self.category_id:
# # # #             raise UserError("Please select a product category.")
        
# # # #         category_id = []
# # # #         if self.category_id:
# # # #             for id in self.category_id:
# # # #                 category_id.append(id.id)

# # # #         customer_id = []
# # # #         if self.customer_id:
# # # #             for id in self.customer_id:
# # # #                 customer_id.append(id.id)

# # # #         product_id = []
# # # #         if self.product_id:
# # # #             for id in self.product_id:
# # # #                 product_id.append(id.id)
        
# # # #         currency_id = []
# # # #         if self.currency_id:
# # # #             for id in self.currency_id:
# # # #                 currency_id.append(id.id)

# # # #         data = {
# # # #             'date_from': self.date_from,
# # # #             'date_to': self.date_to,
# # # #             'cust_sel': self.cust_sel,
# # # #             'prod_sel': self.prod_sel,
# # # #             'category_id': category_id,
# # # #             'customer_id': customer_id,
# # # #             'currency_id': currency_id,
# # # #             'product_id': product_id,
# # # #             'product_code_from': self.product_code_from,
# # # #             'product_code_to': self.product_code_to,
# # # #             # 'invoice_type': self.invocie_type,
            
# # # #         }
# # # #         return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)



# # # from odoo import fields, models
# # # from odoo.exceptions import UserError

# # # class SalesSummaryReportWizard(models.TransientModel):
# # #     _name = 'sales.summary.report'
# # #     _description = 'Sales Summary Report'

# # #     date_from = fields.Date(string='Start Date')
# # #     date_to = fields.Date(string='End Date')
# # #     cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('all customers', 'All Customers')], string='Customer Selection')
# # #     prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
# # #     category_id = fields.Many2many('product.category', string='Product Categories')
# # #     customer_id = fields.Many2many('res.partner', string='Customer')
# # #     product_id = fields.Many2many('product.template', string='Product')
# # #     currency_id = fields.Many2many('res.currency', string='Currency')

# # #     def _get_product_codes(self):
# # #         products = self.env['product.product'].search([])
# # #         unique_codes = set(product.default_code for product in products if product.default_code)
# # #         return [(code, code) for code in sorted(unique_codes)]

# # #     product_code_from = fields.Selection(
# # #         selection='_get_product_codes',
# # #         string='Product Code From'
# # #     )

# # #     product_code_to = fields.Selection(
# # #         selection='_get_product_codes',
# # #         string='Product Code To'
# # #     )

# # #     def _get_customer_codes(self):
# # #         customers = self.env['res.partner'].search([])
# # #         unique_codes = set(customer.x_studio_new_code for customer in customers if customer.x_studio_new_code)
# # #         return [(code, code) for code in sorted(unique_codes)]

# # #     customer_code_from = fields.Selection(
# # #         selection='_get_customer_codes',
# # #         string='Customer Code From'
# # #     )

# # #     customer_code_to = fields.Selection(
# # #         selection='_get_customer_codes',
# # #         string='Customer Code To'
# # #     )

# # #     def print_report(self):
# # #         # Validation
# # #         if self.cust_sel == 'customer wise' and not self.customer_id:
# # #             raise UserError("Please select a customer.")
# # #         if self.prod_sel == 'product wise' and not self.product_id:
# # #             raise UserError("Please select a product.")
# # #         if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
# # #             raise UserError("Please enter both Product Code From and Product Code To.")
# # #         if self.prod_sel == 'category wise' and not self.category_id:
# # #             raise UserError("Please select a product category.")
# # #         if self.cust_sel == 'all customers' and (not self.customer_code_from or not self.customer_code_to):
# # #             raise UserError("Please select both Customer Code From and Customer Code To when 'All Customers' is selected.")

# # #         category_id = []
# # #         if self.category_id:
# # #             for id in self.category_id:
# # #                 category_id.append(id.id)

# # #         customer_id = []
# # #         if self.customer_id:
# # #             for id in self.customer_id:
# # #                 customer_id.append(id.id)

# # #         product_id = []
# # #         if self.product_id:
# # #             for id in self.product_id:
# # #                 product_id.append(id.id)
        
# # #         currency_id = []
# # #         if self.currency_id:
# # #             for id in self.currency_id:
# # #                 currency_id.append(id.id)

# # #         data = {
# # #             'date_from': self.date_from,
# # #             'date_to': self.date_to,
# # #             'cust_sel': self.cust_sel,
# # #             'prod_sel': self.prod_sel,
# # #             'category_id': category_id,
# # #             'customer_id': customer_id,
# # #             'currency_id': currency_id,
# # #             'product_id': product_id,
# # #             'product_code_from': self.product_code_from,
# # #             'product_code_to': self.product_code_to,
# # #             'customer_code_from': self.customer_code_from,
# # #             'customer_code_to': self.customer_code_to,
# # #             # 'invoice_type': self.invoice_type,
            
# # #         }
# # #         return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)










# # from odoo import fields, models
# # from odoo.exceptions import UserError

# # class SalesSummaryReportWizard(models.TransientModel):
# #     _name = 'sales.summary.report'
# #     _description = 'Sales Summary Report'

# #     date_from = fields.Date(string='Start Date')
# #     date_to = fields.Date(string='End Date')
# #     cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('all customers', 'All Customers')], string='Customer Selection')
# #     prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
# #     category_id = fields.Many2many('product.category', string='Product Categories')
# #     customer_id = fields.Many2many('res.partner', string='Customer')
# #     product_id = fields.Many2many('product.template', string='Product')
# #     currency_id = fields.Many2many('res.currency', string='Currency')

# #     # Group By field with default value set to 'product'
# #     group_by = fields.Selection([
# #         ('product', 'Group by Product'),
# #         ('customer', 'Group by Customer')
# #     ], string='Group By', default='product')

# #     def _get_product_codes(self):
# #         products = self.env['product.product'].search([])
# #         unique_codes = set(product.default_code for product in products if product.default_code)
# #         return [(code, code) for code in sorted(unique_codes)]

# #     product_code_from = fields.Selection(
# #         selection='_get_product_codes',
# #         string='Product Code From'
# #     )

# #     product_code_to = fields.Selection(
# #         selection='_get_product_codes',
# #         string='Product Code To'
# #     )

# #     def _get_customer_codes(self):
# #         customers = self.env['res.partner'].search([])
# #         unique_codes = set(customer.x_studio_new_code for customer in customers if customer.x_studio_new_code)
# #         return [(code, code) for code in sorted(unique_codes)]

# #     customer_code_from = fields.Selection(
# #         selection='_get_customer_codes',
# #         string='Customer Code From'
# #     )

# #     customer_code_to = fields.Selection(
# #         selection='_get_customer_codes',
# #         string='Customer Code To'
# #     )

# #     def print_report(self):
# #         # Validation
# #         if self.cust_sel == 'customer wise' and not self.customer_id:
# #             raise UserError("Please select a customer.")
# #         if self.prod_sel == 'product wise' and not self.product_id:
# #             raise UserError("Please select a product.")
# #         if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
# #             raise UserError("Please enter both Product Code From and Product Code To.")
# #         if self.prod_sel == 'category wise' and not self.category_id:
# #             raise UserError("Please select a product category.")
# #         if self.cust_sel == 'all customers' and (not self.customer_code_from or not self.customer_code_to):
# #             raise UserError("Please select both Customer Code From and Customer Code To when 'All Customers' is selected.")

# #         category_id = []
# #         if self.category_id:
# #             for id in self.category_id:
# #                 category_id.append(id.id)

# #         customer_id = []
# #         if self.customer_id:
# #             for id in self.customer_id:
# #                 customer_id.append(id.id)

# #         product_id = []
# #         if self.product_id:
# #             for id in self.product_id:
# #                 product_id.append(id.id)
        
# #         currency_id = []
# #         if self.currency_id:
# #             for id in self.currency_id:
# #                 currency_id.append(id.id)

# #         data = {
# #             'date_from': self.date_from,
# #             'date_to': self.date_to,
# #             'cust_sel': self.cust_sel,
# #             'prod_sel': self.prod_sel,
# #             'category_id': category_id,
# #             'customer_id': customer_id,
# #             'currency_id': currency_id,
# #             'product_id': product_id,
# #             'product_code_from': self.product_code_from,
# #             'product_code_to': self.product_code_to,
# #             'customer_code_from': self.customer_code_from,
# #             'customer_code_to': self.customer_code_to,
# #             'group_by': self.group_by,
# #         }
# #         return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)




# from odoo import fields, models
# from odoo.exceptions import UserError

# class SalesSummaryReportWizard(models.TransientModel):
#     _name = 'sales.summary.report'
#     _description = 'Sales Summary Report'

#     date_from = fields.Date(string='Start Date')
#     date_to = fields.Date(string='End Date')
#     cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('all customers', 'All Customers')], string='Customer Selection')
#     prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
#     category_id = fields.Many2many('product.category', string='Product Categories')
#     customer_id = fields.Many2many('res.partner', string='Customer', domain=[('customer_rank', '>', 0)])
#     product_id = fields.Many2many('product.template', string='Product')
#     currency_id = fields.Many2many('res.currency', string='Currency')

#     group_by = fields.Selection([
#         ('product', 'Group by Product'),
#         ('customer', 'Group by Customer')
#     ], string='Group By', default='product')

#     def _get_product_codes(self):
#         products = self.env['product.product'].search([('sale_ok', '=', True)])
#         return [(product.default_code, "{} - {}".format(product.default_code, product.name))
#                 for product in products if product.default_code]

#     product_code_from = fields.Selection(
#         selection='_get_product_codes',
#         string='Product Code From'
#     )

#     product_code_to = fields.Selection(
#         selection='_get_product_codes',
#         string='Product Code To'
#     )
    
#     def _get_customer_codes(self):
#         customers = self.env['res.partner'].search([('customer_rank', '>', 0)])
#         customer_codes = [
#             (customer.x_studio_new_code, "{} - {}".format(customer.x_studio_new_code, customer.name))
#             for customer in customers if customer.x_studio_new_code
#         ]
#         # Sort by the customer code
#         customer_codes.sort(key=lambda x: x[0])
#         return customer_codes


#     customer_code_from = fields.Selection(
#         selection='_get_customer_codes',
#         string='Customer Code From'
#     )

#     customer_code_to = fields.Selection(
#         selection='_get_customer_codes',
#         string='Customer Code To'
#     )

#     def print_report(self):
#         # Validation
#         if self.cust_sel == 'customer wise' and not self.customer_id:
#             raise UserError("Please select a customer.")
#         if self.prod_sel == 'product wise' and not self.product_id:
#             raise UserError("Please select a product.")
#         if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
#             raise UserError("Please enter both Product Code From and Product Code To.")
#         if self.prod_sel == 'category wise' and not self.category_id:
#             raise UserError("Please select a product category.")
#         if self.cust_sel == 'all customers' and (not self.customer_code_from or not self.customer_code_to):
#             raise UserError("Please select both Customer Code From and Customer Code To when 'All Customers' is selected.")

#         category_id = []
#         if self.category_id:
#             for id in self.category_id:
#                 category_id.append(id.id)

#         customer_id = []
#         if self.customer_id:
#             for id in self.customer_id:
#                 customer_id.append(id.id)

#         product_id = []
#         if self.product_id:
#             for id in self.product_id:
#                 product_id.append(id.id)
        
#         currency_id = []
#         if self.currency_id:
#             for id in self.currency_id:
#                 currency_id.append(id.id)

#         data = {
#             'date_from': self.date_from,
#             'date_to': self.date_to,
#             'cust_sel': self.cust_sel,
#             'prod_sel': self.prod_sel,
#             'category_id': category_id,
#             'customer_id': customer_id,
#             'currency_id': currency_id,
#             'product_id': product_id,
#             'product_code_from': self.product_code_from,
#             'product_code_to': self.product_code_to,
#             'customer_code_from': self.customer_code_from,
#             'customer_code_to': self.customer_code_to,
#             'group_by': self.group_by,
#         }
#         return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)




from odoo import fields, models
from odoo.exceptions import UserError

class SalesSummaryReportWizard(models.TransientModel):
    _name = 'sales.summary.report'
    _description = 'Sales Summary Report'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    cust_sel = fields.Selection([('customer wise', 'Customer Wise'), ('range wise', 'Range Wise')], string='Customer Selection')
    prod_sel = fields.Selection([('product wise', 'Product Wise'), ('range wise', 'Range Wise'), ('category wise', 'Category Wise')], string='Product Selection')
    category_id = fields.Many2many('product.category', string='Product Categories')
    customer_id = fields.Many2many('res.partner', string='Customer', domain=[('customer_rank', '>', 0)])
    currency_id = fields.Many2many('res.currency', string='Currency')

    group_by = fields.Selection([
        ('product', 'Group by Product'),
        ('customer', 'Group by Customer')
    ], string='Group By', default='product')

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

    def _get_customer_codes(self):
        customers = self.env['res.partner'].search([('customer_rank', '>', 0)])
        customer_codes = [
            (customer.x_studio_new_code, "{} - {}".format(customer.x_studio_new_code, customer.name))
            for customer in customers if customer.x_studio_new_code
        ]
        customer_codes.sort(key=lambda x: x[0])
        return customer_codes

    customer_code_from = fields.Selection(
        selection='_get_customer_codes',
        string='Customer Code From'
    )

    customer_code_to = fields.Selection(
        selection='_get_customer_codes',
        string='Customer Code To'
    )

    def print_report(self):
        # Validation
        if self.cust_sel == 'customer wise' and not self.customer_id:
            raise UserError("Please select a customer.")
        if self.prod_sel == 'product wise' and not self.product_id:
            raise UserError("Please select a product.")
        if self.prod_sel == 'range wise' and (not self.product_code_from or not self.product_code_to):
            raise UserError("Please enter both Product Code From and Product Code To.")
        if self.prod_sel == 'category wise' and not self.category_id:
            raise UserError("Please select a product category.")
        if self.cust_sel == 'all customers' and (not self.customer_code_from or not self.customer_code_to):
            raise UserError("Please select both Customer Code From and Customer Code To when 'All Customers' is selected.")

        category_id = [cat.id for cat in self.category_id] if self.category_id else []

        customer_id = [cust.id for cust in self.customer_id] if self.customer_id else []

        product_id = [prod.id for prod in self.product_id] if self.product_id else []
        
        currency_id = [curr.id for curr in self.currency_id] if self.currency_id else []

        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'cust_sel': self.cust_sel,
            'prod_sel': self.prod_sel,
            'category_id': category_id,
            'customer_id': customer_id,
            'currency_id': currency_id,
            'product_id': product_id,
            'product_code_from': self.product_code_from,
            'product_code_to': self.product_code_to,
            'customer_code_from': self.customer_code_from,
            'customer_code_to': self.customer_code_to,
            'group_by': self.group_by,
        }
        return self.env.ref('sales_summary.sales_summary_report_pdf').with_context(landscape=True).report_action(self, data=data)
