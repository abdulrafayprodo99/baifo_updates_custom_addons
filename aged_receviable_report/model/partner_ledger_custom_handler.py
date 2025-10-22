# from odoo import fields, api, models
# from odoo.exceptions import UserError, ValidationError
# import json
# from datetime import date

# class InheritPartnerLedger(models.TransientModel):
#     _name = "partner.ledger.report"
#     _description = 'Partner Ledger Wizard'

#     supplier_ids=fields.Many2many(string="Suppliers",comodel_name='res.partner',required=True)

#     from_date=fields.Date(string="From Date", required=True)
#     to_date=fields.Date(string="to Date", required=True)
    
#     # from_supplier=fields.Selection(selection='supplier_selection', string="From Supplier")
#     # to_supplier=fields.Selection(selection='supplier_selection', string="To Supplier")

#     # from_supplier_id=fields.Char()
#     # to_supplier_id=fields.Char()
    
#     # @api.onchange("from_supplier","to_supplier")
#     # def save_key(self):
#     #     self.from_supplier_id=self.from_supplier
#     #     self.to_supplier_id=self.to_supplier

#     # def supplier_selection(self):
#     #     return sorted([(sup.id, f"{sup.id}-{sup.name}") 
#     #             for sup in self.env['res.partner'].search([("supplier_rank",">",0),("is_company","=",True)])])
    
#     @api.onchange("from_date","to_date")
#     def on_change(self):
#         if self.from_date == False:
#             self.from_date=''
#         if self.to_date == False:
#             self.to_date=''
#         # if self.from_supplier == False:
#         #     self.from_supplier=''
#         # if self.to_supplier == False:
#         #     self.to_supplier=''

#     date = fields.Boolean('Date', default=True)
#     doc = fields.Boolean('Document No',default=True)
#     # ref = fields.Boolean('Reference')
#     narration = fields.Boolean('Narration',default=True)
#     product_code = fields.Boolean('Product Code',default=True)
#     product_description = fields.Boolean('Product Description',default=True)
#     unit = fields.Boolean('Unit',default=True)
#     quantity = fields.Boolean('Qty',default=True)
#     rate = fields.Boolean('Rate',default=True)
#     excluding_sale_tax = fields.Boolean('Value Excluding Sales Tax',default=True)
#     sale_tax_amount = fields.Boolean('Sales Tax Amount',default=True)
#     debit = fields.Boolean('Debit',default=True)
#     credit = fields.Boolean('Credit',default=True)
#     balance = fields.Boolean('Closing Balance',default=True)

#     def action_supplier(self):
#         column_true = []
#         for field_name in self._fields:
#             if isinstance(self._fields[field_name], fields.Boolean) and getattr(self, field_name):
#                 column_true.append(field_name)

#         supplier_ids=[]
#         for id in self.supplier_ids:
#             supplier_ids.append(id.id)

#         # raise UserError(f"{self.env['res.partner'].browse(supplier_ids[0]).name}")
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'aged_receivable_report.action_supplier_ledger_report',
#             'params':{
#                 'column':column_true,
#                 'supplier_id1': self.env['res.partner'].browse(supplier_ids[0]).name,
#                 'supplier_id2': self.env['res.partner'].browse(supplier_ids[len(supplier_ids)-1]).name,
#                 'from_date': self.from_date,
#                 'to_date': self.to_date,
#                 'suppliers': supplier_ids
#             }
#         }





from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
from datetime import date

class InheritPartnerLedger(models.TransientModel):
    _name = "partner.ledger.report"
    _description = 'Partner Ledger Wizard'

    # Supplier selection fields
    supplier_ids = fields.Many2many(
        string="Partners",
        comodel_name='res.partner',
    )

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    
    # Selection mode (range or supplier list)
    selection_mode = fields.Selection(
        [('supplier_ids', 'Partner List'), ('range', 'Range')],
        string="Selection Mode",
        default='supplier_ids',
        required=True
    )

    # Sorted supplier range selection fields
    from_supplier = fields.Selection(
        selection='_get_sorted_suppliers',
        string="From Partner"
    )
    to_supplier = fields.Selection(
        selection='_get_sorted_suppliers',
        string="To Partner"
    )

    @api.model
    def _get_sorted_suppliers(self):
        # Get suppliers with supplier_rank > 0 and sorted by x_studio_new_code
        suppliers = self.env['res.partner'].search(
            [("supplier_rank", ">", 0), ("is_company", "=", True)],
            order="x_studio_new_code asc"
        )
        return [(sup.id, f"{sup.x_studio_new_code} - {sup.name}") for sup in suppliers]

    @api.onchange("from_date", "to_date")
    def on_change(self):
        if not self.from_date:
            self.from_date = ''
        if not self.to_date:
            self.to_date = ''

    # Column boolean fields
    date = fields.Boolean('Date', default=True)
    doc = fields.Boolean('Document No', default=True)
    narration = fields.Boolean('Narration', default=True)
    product_code = fields.Boolean('Product Code', default=True)
    product_description = fields.Boolean('Product Description', default=True)
    unit = fields.Boolean('Unit', default=True)
    quantity = fields.Boolean('Qty', default=True)
    rate = fields.Boolean('Rate', default=True)
    excluding_sale_tax = fields.Boolean('Value Excluding Sales Tax', default=True)
    sale_tax_amount = fields.Boolean('Sales Tax Amount', default=True)
    debit = fields.Boolean('Debit', default=True)
    credit = fields.Boolean('Credit', default=True)
    balance = fields.Boolean('Closing Balance', default=True)

    def action_supplier(self):
        # Get list of boolean fields set to True
        column_true = [
            field_name for field_name in self._fields 
            if isinstance(self._fields[field_name], fields.Boolean) and getattr(self, field_name)
        ]

        # Determine supplier list based on selection mode
        supplier_ids = []
        if self.selection_mode == 'supplier_ids':
            supplier_ids = [supplier.id for supplier in self.supplier_ids]
        elif self.selection_mode == 'range':
            # Retrieve suppliers within the "From Supplier" and "To Supplier" range based on x_studio_new_code
            from_supplier = self.env['res.partner'].browse(int(self.from_supplier)) if self.from_supplier else None
            to_supplier = self.env['res.partner'].browse(int(self.to_supplier)) if self.to_supplier else None
            
            if from_supplier and to_supplier:
                supplier_ids = self.env['res.partner'].search([
                    ("supplier_rank", ">", 0),
                    ("is_company", "=", True),
                    ("x_studio_new_code", ">=", from_supplier.x_studio_new_code),
                    ("x_studio_new_code", "<=", to_supplier.x_studio_new_code)
                ]).ids

        return {
            'type': 'ir.actions.client',
            'tag': 'aged_receivable_report.action_supplier_ledger_report',
            'params': {
                'column': column_true,
                'supplier_id1': self.from_supplier if self.selection_mode == 'range' else '',
                'supplier_id2': self.to_supplier if self.selection_mode == 'range' else '',
                'from_date': self.from_date,
                'to_date': self.to_date,
                'suppliers': supplier_ids
            }
        }
