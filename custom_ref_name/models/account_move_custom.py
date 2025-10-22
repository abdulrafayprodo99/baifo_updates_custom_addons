# # # # from odoo import models, fields, api
# # # # from odoo.exceptions import UserError

# # # # class AccountMove(models.Model):
# # # #     _inherit = 'account.move'

# # # #     # Define asset_id first to ensure related fields can reference it
# # # #     asset_id = fields.Many2one('account.asset', string='Asset')

# # # #     # # Directly related fields to asset_id
# # # #     # sr_no = fields.Integer(related='asset_id.sr_no', string='Serial Number', readonly=True)
# # # #     # asset_tag = fields.Char(related='asset_id.asset_tag', string='Asset Tag', readonly=True)

# # # #     @api.depends('ref')
# # # #     def _compute_ref(self):

# # # #         for move in self:
# # # #             # raise UserError(str(move.asset_id[0].sr_no))
# # # #             # raise UserError(str(move.asset_id[0].name))


# # # #             ref = move.asset_id[0].name or ''
# # # #             sr_no = str(move.asset_id[0].sr_no) if move.asset_id[0].sr_no else ''
# # # #             asset_tag = move.asset_id[0].asset_tag or ''
# # # #             move.ref = f"{ref}: Depreciation / {sr_no} / {asset_tag}" if sr_no or asset_tag else ref

# # # #     # Override the ref field to compute it
# # # #     ref = fields.Char(string='Reference', compute='_compute_ref')


# # # # class AccountMoveLine(models.Model):
# # # #     _inherit = 'account.move.line'

# # # #     # Define asset_id first to ensure related fields can reference it
# # # #     asset_id = fields.Many2one('account.asset', string='Asset')

# # # #     # # Directly related fields to asset_id
# # # #     # sr_no = fields.Integer(related='asset_id.sr_no', string='Serial Number', readonly=True)
# # # #     # asset_tag = fields.Char(related='asset_id.asset_tag', string='Asset Tag', readonly=True)

# # # #     # @api.depends('amount_currency', 'tax_ids')
# # # #     # def _compute_name(self):

# # # #     #     raise UserError("hello!!")
# # # #     #     for line in self:
# # # #     #         raise UserError(str(line))
# # # #     # #         # name = line.name or ''
# # # #     # #         # sr_no = str(line.sr_no) if line.sr_no else ''
# # # #     # #         # asset_tag = line.asset_tag or ''
# # # #     # #         # line.name = f"{name} / {sr_no} / {asset_tag}" if sr_no or asset_tag else name

# # # #     # # # Override the name field to compute it
# # # #     # name = fields.Char(string='Label', compute='_compute_name')



# # # from odoo import models, fields, api
# # # from odoo.exceptions import UserError

# # # class AccountMove(models.Model):
# # #     _inherit = 'account.move'

# # #     # Define asset_id first to ensure related fields can reference it
# # #     asset_id = fields.Many2one('account.asset', string='Asset')

# # #     @api.depends('ref')
# # #     def _compute_ref(self):
# # #         for move in self:
# # #             ref = move.asset_id[0].name if move.asset_id else ''
# # #             sr_no = str(move.asset_id[0].sr_no) if move.asset_id and move.asset_id.sr_no else ''
# # #             asset_tag = move.asset_id[0].asset_tag if move.asset_id else ''
# # #             move.ref = f"{ref}: Depreciation / {sr_no} / {asset_tag}" if sr_no or asset_tag else ref

# # #     # Override the ref field to compute it
# # #     ref = fields.Char(string='Reference', compute='_compute_ref')

# # # class AccountMoveLine(models.Model):
# # #     _inherit = 'account.move.line'

# # #     # Define asset_id first to ensure related fields can reference it
# # #     asset_id = fields.Many2one('account.asset', string='Asset')

# # #     # Override the name field to compute it based on the related move's ref field
# # #     name_2 = fields.Char(string='Label', compute='_compute_name')

# # #     @api.depends('move_id')
# # #     def _compute_name(self):
# # #         # raise UserError("helllo")
# # #         for line in self:
# # #             ref = line.asset_id[0].name if line.asset_id else ''
# # #             raise UserError(str(ref))

# # #             # Set name to the ref field of the related account.move record
# # #             line.name = line.move_id.ref if line.move_id else ''

# # from odoo import models, fields, api

# # class AccountMove(models.Model):
# #     _inherit = 'account.move'

# #     # Define asset_id first to ensure related fields can reference it
# #     asset_id = fields.Many2one('account.asset', string='Asset')

# #     @api.depends('asset_id')
# #     def _compute_ref(self):
# #         for move in self:
# #             ref = move.asset_id.name if move.asset_id else ''
# #             sr_no = str(move.asset_id.sr_no) if move.asset_id and move.asset_id.sr_no else ''
# #             asset_tag = move.asset_id.asset_tag if move.asset_id else ''
# #             move.ref = f"{ref}: Depreciation / {sr_no} / {asset_tag}" if sr_no or asset_tag else ref

# #     # Override the ref field to compute it
# #     ref = fields.Char(string='Reference', compute='_compute_ref')

# # class AccountMoveLine(models.Model):
# #     _inherit = 'account.move.line'

# #     # Define asset_id first to ensure related fields can reference it
# #     asset_id = fields.Many2one('account.asset', string='Asset')

# #     # Override the name field to compute it based on the related move's ref field
# #     name_2 = fields.Char(string='Label', compute='_compute_name')

# #     @api.depends('move_id.ref')
# #     def _compute_name(self):
# #         for line in self:
# #             # Set name_2 to the ref field of the related account.move record
# #             line.name_2 = line.move_id.ref if line.move_id else ''

# from odoo import models, fields, api

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     # Define asset_id first to ensure related fields can reference it
#     asset_id = fields.Many2one('account.asset', string='Asset')

#     # @api.depends('asset_id')
#     # def _compute_ref(self):
#     #     for move in self:
#     #         ref = move.asset_id.name if move.asset_id else ''
#     #         sr_no = str(move.asset_id.sr_no) if move.asset_id and move.asset_id.sr_no else ''
#     #         asset_tag = move.asset_id.asset_tag if move.asset_id else ''
#     #         move.ref = f"{ref}: Depreciation / {sr_no} / {asset_tag}" if sr_no or asset_tag else ref

#     # # Override the ref field to compute it
#     # ref = fields.Char(string='Reference', compute='_compute_ref', readonly=False)

# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'

#     # Define asset_id first to ensure related fields can reference it
#     asset_id = fields.Many2one('account.asset', string='Asset')

#     # Override the name field to compute it based on the related move's ref field
#     name_2 = fields.Char(string='Label', compute='_compute_name')

#     @api.depends('move_id.ref')
#     def _compute_name(self):
#         for line in self:
#             if line.move_id and line.move_id.ref:
#                 # Remove ': Depreciation' from ref if present
#                 ref = line.move_id.ref.replace(': Depreciation', '').strip()
#             else:
#                 ref = ''
#             line.name_2 = ref







from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Define asset_id first to ensure related fields can reference it
    asset_id = fields.Many2one('account.asset', string='Asset')

    # ref_name_2 = fields.Char(string='Ref', compute='_compute_name')

    @api.depends('asset_id')
    def _compute_ref(self):
        for move in self:
            ref = move.asset_id.name if move.asset_id else ''
            sr_no = str(move.asset_id.sr_no) if move.asset_id and move.asset_id.sr_no else ''
            asset_tag = move.asset_id.asset_tag if move.asset_id else ''
            move.ref_name_2 = f"{ref}: Depreciation / {sr_no} / {asset_tag}" if sr_no or asset_tag else ref

    # Override the ref field to compute it
    ref_name_2 = fields.Char(string='Reference', compute='_compute_ref', readonly=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Define asset_id first to ensure related fields can reference it
    asset_id = fields.Many2one('account.asset', string='Asset')

    # Override the name field to compute it based on the related move's ref field
    name_2 = fields.Char(string='Label', compute='_compute_name')

    @api.depends('move_id.ref')
    def _compute_name(self):
        for line in self:
            if line.move_id and line.move_id.ref_name_2:
                # Remove ': Depreciation' from ref if present
                ref = line.move_id.ref_name_2.replace(': Depreciation', '').strip()
            else:
                ref = ''
            line.name_2 = ref