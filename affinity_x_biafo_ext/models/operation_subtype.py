from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime


class OperationSubtype(models.Model):
    _name = "operation.subtype"
    _description = "Operation Subytype"

    name = fields.Char(string='Name', required=True)
    prefix =fields.Char(string='Prefix')
    status = fields.Selection([('lot has not been created','Lot Has Not Been Created'),('lot has been created','Lot Has Been Created')], string = 'Status' , default = 'lot has not been created')

    

    def update_seq(self):
        # next_sequence = self.env['ir.sequence'].next_by_code('seq')
        existing_record = self.env['ir.sequence'].search([('code', '=', self.prefix)])
        


        # if not existing_record:
        #     new_record_vals = {
        #         'prefix': self.prefix,
        #         'code' : self.prefix,
        #         'name': 'Operation SubType - ' + str(self.prefix),
        #         'number_increment' : 1,
        #         'padding' : 5
        #     }
        #     new_record = self.env['ir.sequence'].create(new_record_vals)
        #     self['status'] = 'lot has been created'
        # else:
        #     raise UserError('lot has already been created')
            

    # # @api.model        
    # def update_button(self):
    #      if self.status == 'lot has been created':
    #             raise UserError('lot has already been created')
            


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    operation_subtype = fields.Many2one('operation.subtype',string="Subtype")
    # operation_subtype = fields.Char(string="Subtype")
    

class MrpProduction(models.Model):
    _inherit = "mrp.production"


    # def _prepare_stock_lot_values(self):
    #     res = super(MrpProduction, self)._prepare_stock_lot_values()

    #     self.ensure_one()
    #     if self.product_id.tracking == 'lot':
    #         self.product_id.update_number_next()
    #         # raise UserError(str(self['product_id']['next_seq_number']).rjust(3, '0'))
    #         current_datetime = datetime.now()
    #         res['name'] = str(self['product_id']["default_code"]) + '-' + current_datetime.strftime("%d%m%y") + '-' + str(self['product_id']['next_seq_number']).rjust(4, '0')#str(self.env['ir.sequence'].next_by_code('seq_bom_x'))
    #         exist_lot = self.env['stock.lot'].search([
    #             ('product_id', '=', self.product_id.id),
    #             ('company_id', '=', self.company_id.id),
    #             ('name', '=', res['name']),
    #         ], limit=1)
    #         if exist_lot:
    #             res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
    #     else:
    #         res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
    #     # raise UserError(str(res))
    #     return {
    #         'product_id': self.product_id.id,
    #         'company_id': self.company_id.id,
    #         'name': res['name'],
    #     }
    def _prepare_stock_lot_values(self):
        res = super(MrpProduction, self)._prepare_stock_lot_values()

        self.ensure_one()
        
        current_datetime = datetime.now()
        current_fiscal_year = current_datetime.year
        
        # Check if it's a new fiscal year
        if self.product_id.tracking == 'lot':
            # Check if we need to reset the sequence
            if self.product_id.last_reset_year != current_fiscal_year:
                self.product_id.write({
                    'next_seq_number': 1,
                    'last_reset_year': current_fiscal_year
                })
            else:
                self.product_id.update_number_next()
            
            # Generate the lot name
            res['name'] = (
                f"{self.product_id.default_code}-"
                f"{current_datetime.strftime('%d%m%y')}-"
                f"{str(self.product_id.next_seq_number).rjust(4, '0')}"
            )

            exist_lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
                ('name', '=', res['name']),
            ], limit=1)
            
            if exist_lot:
                res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
        else:
            res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
        
        return {
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': res['name'],
        }

    # # Bilal End

class ProductProduct(models.Model):
    _inherit="product.product"

    # next_seq_number = fields.Integer(string="Next Sequence Number")

    next_seq_number = fields.Integer(string='Next Sequence Number', default=1)
    last_reset_year = fields.Integer(string='Last Reset Year', default=lambda self: datetime.now().year)
    # def update_number_next(self):
        
    #     new_number_next = self.next_seq_number + 1
    #     double_padded_number_next = str(new_number_next).rjust(3, '0')
    #     # raise UserError(int(double_padded_number_next))
    #     self.write({'next_seq_number': int(double_padded_number_next)})

    def update_number_next(self):
        new_number_next = self.next_seq_number + 1
        double_padded_number_next = str(new_number_next).rjust(3, '0')
        self.write({'next_seq_number': int(double_padded_number_next)})