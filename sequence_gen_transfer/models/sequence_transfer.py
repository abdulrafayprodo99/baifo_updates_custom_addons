# from odoo  import models,  fields, api
# from odoo.exceptions import UserError


# class StockPicking(models.Model):
#     _inherit = "stock.picking"

#     # sher ahmed
#     temp_name = fields.Char(string="temp number")
#     seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)
    
    # @api.depends("state")
    # sher ahmed
    # def compute_temp_no(self):
#         for rec in self:
#             raise UserError([str(rec.read())])
#             if not rec.seq_generate:

#                 current_date = self.date
#                 current_year = current_date.year
#                 current_month = current_date.month
#                 # sequence_code = rec.journal_id.sequence_id.code
#                 # sequence = rec.journal_id.sequence_id.next_by_code(sequence_code, sequence_date=current_date)
   
#                 if rec.payment_type == 'inbound':
#                     sequence_code = rec.journal_id.sequence_id_2.code
#                     sequence = rec.journal_id.sequence_id_2.next_by_code(sequence_code, sequence_date=current_date)
                    
#                     rec['temp_name'] = f"{rec.journal_id.customer_payment_code}-{current_year}-{current_month}-{sequence}"
#                 else:
#                     sequence_code = rec.journal_id.sequence_id.code
#                     sequence = rec.journal_id.sequence_id.next_by_code(sequence_code, sequence_date=current_date)
#                     rec['temp_name'] = f"{rec.journal_id.sequence_code_short}-{current_year}-{current_month}-{sequence}"
                    
#                 rec['seq_generate'] = True
#                 self.name=self.temp_name
#             else:
#                 if not rec.temp_name:
#                     rec['temp_name'] = ""
        
    

        
    # def action_prepare(self):
    # #    self['approval_state']='prepared'
    # #    self['prepared_by'] = self.write_uid.id
    # #    self['prepared_timestamp'] = fields.Datetime.now()

    #    self.compute_temp_no()




# # -*- coding: utf-8 -*-
# from odoo import api, fields, models, _
# from odoo.exceptions import UserError

# class StockPicking(models.Model):
#     _inherit = "stock.picking"

#     temp_name = fields.Char(string="Temporary Sequence")
#     seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)

#     def compute_temp_no(self):
#         for rec in self:
#             if not rec.seq_generate:
#                 current_date = fields.Date.context_today(self)
#                 current_year = current_date.year

#                 # Pad the month to ensure it is two digits (e.g., 01, 02, ..., 12)
#                 current_month = str(current_date.month).zfill(2)

#                 # Get the prefix from sequence_code field on stock.picking.type
#                 prefix = rec.picking_type_id.sequence_code or ""

#                 if not prefix:
#                     raise UserError(_("Sequence Code is missing in the picking type."))

#                 sequence = rec.picking_type_id.sequence_id._get_current_sequence()
#                 if not sequence:
#                     raise UserError(_("No sequence found for the current date range."))

#                 # Get the padding from the sequence (e.g., 4 means it will pad to 4 digits)
#                 padding = rec.picking_type_id.sequence_id.padding or 0

#                 # Get number_next_actual from ir.sequence.date_range and apply padding
#                 number_next_actual = str(sequence.number_next_actual).zfill(padding)  # Dynamic padding based on the sequence's padding

#                 # Generate temp name with custom prefix, year, padded month, and padded sequence number
#                 rec.temp_name = f"{prefix}-{current_year}-{current_month}-{number_next_actual}"

#                 rec.seq_generate = True
#                 rec.name = rec.temp_name
#             else:
#                 if not rec.temp_name:
#                     rec.temp_name = ""



# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    temp_name = fields.Char(string="Temporary Sequence")
    seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)

    def compute_temp_no(self):
        for rec in self:
            if not rec.seq_generate:
                current_date = fields.Date.context_today(self)
                current_year = current_date.year

                # Pad the month to ensure it is two digits (e.g., 01, 02, ..., 12)
                current_month = str(current_date.month).zfill(2)

                # Get the prefix from sequence_code field on stock.picking.type
                prefix = rec.picking_type_id.sequence_code or ""

                if not prefix:
                    raise UserError(_("Sequence Code is missing in the picking type."))

                sequence = rec.picking_type_id.sequence_id._get_current_sequence()
                if not sequence:
                    raise UserError(_("No sequence found for the current date range."))

                # Get the padding from the sequence (e.g., 4 means it will pad to 4 digits)
                # padding = sequence.padding or 0
                # Get the padding from the sequence (e.g., 4 means it will pad to 4 digits)
                padding = rec.picking_type_id.sequence_id.padding or 0
                # raise UserError(sequence.number_next_actual)
                # Fetch the next number from the sequence using number_next (not number_next_actual)
                number_next_actual = str(sequence.number_next_actual).zfill(padding)  # Dynamic padding based on the sequence's padding

                # Generate temp name with custom prefix, year, padded month, and padded sequence number
                rec.temp_name = f"{prefix}{current_year}-{current_month}-{number_next_actual}"
                sequence.sudo().number_next_actual += 1

                # Odoo automatically increments the sequence, so no manual increment needed here
                rec.seq_generate = True
                rec.name = rec.temp_name
            else:
                if not rec.temp_name:
                    rec.temp_name = ""




    # def button_validate(self):
    #     for rec in self:
    #         if not rec.seq_generate:
    #             rec._generate_sequence()
    #     return super(StockPicking, self).button_validate()

    # def action_prepare(self):
    #     # Call the original action_prepare logic (if it exists)
    #     # res = super(StockPicking, self).action_prepare()

    #     # # Call the sequence generation logic
    #     # for rec in self:
    #     #     if not rec.seq_generate:
    #     #         rec._generate_sequence()

    #     # return res

    #     self._generate_sequence()


    # def action_prepare2(self):
    #     self['approval_state'] = 'prepared'
    #     self['prepared_by_2'] = self.write_uid.id
    #     self['prepared_timestamp'] = fields.Datetime.now()

    #     # Check if the operation is an internal transfer
    #     if self.picking_type_id.code != 'outgoing':
    #         self.compute_temp_no()



    # def action_prepare1(self):
    #     self['dispatch_approval'] = 'prepared'
    #     self['prepared_by1'] = self.write_uid.id
    #     self['prepared_timestamp1'] = fields.Datetime.now()
    #     self['readonly_check'] = True

    #     # Check if the operation is a Delivery Order (DO)
    #     if self.picking_type_id.code == 'outgoing':
    #         self.compute_temp_no()
