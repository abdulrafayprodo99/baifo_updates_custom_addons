from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    asset_name = fields.Char('Asset Name',readonly=False)
    actual_value = fields.Monetary(related='asset_id.original_value', string='Actual Value')
    current_value = fields.Monetary(string='Current Value', compute='_compute_asset_transfer')
    depreciated_value = fields.Monetary(string='Depreciated Value', compute='_compute_asset_transfer')

    asset_model_id = fields.Many2one(
        'account.asset',
        string='Asset Model',
        domain=[('state', '=', 'model')],
        compute='compute_current_asset_model_id',
        store=True,
        readonly=False

    )
    fixed_asset_account = fields.Many2one('account.account', related='asset_model_id.account_asset_id')
    dep_asset_account = fields.Many2one('account.account', related='asset_model_id.account_depreciation_id')
    exp_asset_account = fields.Many2one('account.account', related='asset_model_id.account_depreciation_expense_id')
    transfer_date = fields.Date(string='Transfer Date')

    asset_method = fields.Selection(
        selection=[
            ('linear', 'Straight Line'),
            ('degressive', 'Declining'),
            ('degressive_then_linear', 'Declining then Straight Line')
        ],
        string='Method',
    )
    asset_progress_factor = fields.Float(string="Declining Factor", default=0.3)
    asset_prorata_computation_type = fields.Selection(
        selection=[
            ('none', 'No Prorata'),
            ('constant_periods', 'Constant Periods'),
            ('daily_computation', 'Based on days per period'),
        ], string='Prorata Computation')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get('params').get('id')
        active_model = self.env.context.get('params').get('model')
        if active_id:
            asset = self.env[active_model].browse(active_id)
            res.update({
                'asset_name':f'{asset.name} - OWN',
                'asset_method': asset.method,
                'asset_progress_factor': asset.method_progress_factor,
                'asset_prorata_computation_type': asset.prorata_computation_type,
            })
        return res

    @api.depends('asset_id')
    def _get_selection_modify_options(self):
        selection = super(AssetModify, self)._get_selection_modify_options()
        if ('asset_transfer', _('Asset Transfer')) not in selection:
            selection.append(('asset_transfer', _('Asset Transfer')))

        return selection

    @api.depends('asset_id')
    def _compute_asset_transfer(self):
        posted_value = self.env['account.move'].search([('state', '=', 'posted'), ('asset_id', '=', self.asset_id.id)],
                                                       limit=1,
                                                       order="id desc")
        self.current_value = posted_value.asset_remaining_value
        self.depreciated_value = posted_value.asset_depreciated_value + self.asset_id.opening_accumulated_depreciation

    @api.depends('asset_id')
    def compute_current_asset_model_id(self):
        current_asset_model = self.asset_id.model_id
        self.asset_model_id = current_asset_model.id

    def attach_jv_to_asset(self, jv, account_asset):
        last_dep_debit = jv.line_ids.filtered(
            lambda line_item: line_item.account_id.id == self.fixed_asset_account.id and
                              line_item.debit == self.current_value
        )
        account_asset.write({
            'original_move_line_ids': [(6, 0, last_dep_debit.ids)]
        })
        # account_asset.original_move_line_ids.ids = last_dep_debit.ids

    def create_jv(self):
        journal_entry = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': self.asset_model_id.journal_id.id,
            'date': self.transfer_date,
            'ref': f'Asset Transfer Entry for {self.asset_name}',
        })

        # Step 2: Create the Journal Items (Lines)
        lines = [
            # 1 asset selected model accoun t
            (0, 0, {
                'account_id': self.asset_id.model_id.account_asset_id.id,
                'credit': self.current_value,
                'debit': 0.0,
                'name': 'Credit Current Value',
            }),
            (0, 0, {
                'account_id': self.asset_id.model_id.account_asset_id.id,
                'credit': self.depreciated_value,
                'debit': 0.0,
                'name': 'Credit Depreciated Value',
            }),
            (0, 0, {
                'account_id': self.asset_id.model_id.account_depreciation_id.id,
                'debit': self.depreciated_value,
                'credit': 0.0,
                'name': 'Debit Depreciated Value',
            }),
            # 2 current selected model
            (0, 0, {
                'account_id': self.asset_model_id.account_asset_id.id,
                'debit': self.current_value,
                'credit': 0.0,
                'name': 'Debit Depreciated Value',
            }),
            (0, 0, {
                'account_id': self.asset_model_id.account_asset_id.id,
                'debit': self.depreciated_value,
                'credit': 0.0,
                'name': 'Debit Depreciated Value',
            }),
            (0, 0, {
                'account_id': self.asset_model_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': self.depreciated_value,
                'name': 'Debit Depreciated Value',
            }),
        ]

        # Step 3: Attach Lines to Move
        journal_entry.write({'line_ids': lines})
        journal_entry.action_post()
        return journal_entry

    def validate_asset_transfer(self):
        jv = self.create_jv()
        account_asset = self.env['account.asset'].create({
            'name': self.asset_name,
            'original_value': self.current_value,
            'model_id': self.asset_model_id.id,
        })
        account_asset._onchange_model_id()
        account_asset.write({
            'method': self.asset_method,
            'method_progress_factor': self.asset_progress_factor,
            'prorata_computation_type': self.asset_prorata_computation_type,
            'method_number': self.method_number
        })
        self.attach_jv_to_asset(jv, account_asset)
        account_asset.validate()
        self.asset_id.depreciation_move_ids = [(4, jv.id)]

