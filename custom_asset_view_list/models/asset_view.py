from odoo import models, fields , _ ,api
from odoo.exceptions import UserError
from datetime import datetime



class AccountAsset(models.Model):
    _inherit = 'account.asset'


    old_asset_original_value = fields.Float(string="Opening Asset Value")
    sr_no = fields.Integer(string="Asset ID" , readonly=True)
    original_value = fields.Monetary(string="Opening Depricated Value", compute='_compute_value', store=True, states={'draft': [('readonly', False)]})
    model_id = fields.Many2one('account.asset', string="Asset Model", change_default=True, readonly=True, states={'draft': [('readonly', False)]}, domain="[('company_id', '=', company_id)]")
    asset_class = fields.Char(string='Asset Class')
    sub_asset_class = fields.Char(string='Sub Asset Class')
    asset_tag = fields.Char(string="Asset Tag")
    depreciation_disposal=fields.Float("Depreciation on Disposal")


    
    depreciation_for_the_period = fields.Float(
        string='Depreciation for the Period',
        compute='_compute_depreciation_for_the_period',
    )

    def depreciation_field_population(self):
        for rec  in self:
            asset_id=rec.account_asset_id
            dep_id=rec.account_depreciation_id
            journal_entry=rec.depreciation_move_ids.filtered(lambda line : 'Sale' in line.ref)
            if journal_entry:
                disposal=journal_entry.line_ids.filtered(lambda line : line.account_id==asset_id and line.credit>0)
                depreciation_disposal=journal_entry.line_ids.filtered(lambda line : line.account_id==dep_id)
                if disposal:
                    rec.disposal=disposal.credit
                if depreciation_disposal:
                    rec.depreciation_disposal=depreciation_disposal.debit

                return True
            return False

    @api.depends('sr_no')  # Ensure this method is triggered on changes to the asset
    def _compute_depreciation_for_the_period(self):
        for asset in self:
            journal_entries = self.env['account.move'].search([
                ('asset_id', '=', asset.id),
                ('state', '=', 'posted')    
            ])
            if asset.state == 'close':
                journal_entries = journal_entries.filtered(lambda x: 'depreciation' in str(x.ref).lower())
            total_depreciation = sum(journal_entries.mapped('amount_total_signed'))  
            asset.depreciation_for_the_period = total_depreciation
        

    opening_accumulated_depreciation = fields.Float(string='Opening Accumulated Depreciation', compute='_compute_opening_accumulated_depreciation')
    closing_accumulated_depreciation = fields.Float(string='Closing Accumulated Depreciation', compute='_compute_closing_accumulated_depreciation')
    wdv = fields.Float(string='WDV', compute='_compute_wdv')
    disposal = fields.Float(string='Disposal')

    additions_disposals = fields.Monetary(
        string="Additions/Disposals",
        compute="_compute_additions_disposals",
        currency_field='currency_id',
        store=False  
    )
 

    close_asset_value = fields.Monetary(
        string="Close Asset Value",
        compute="_compute_close_asset_value",
        currency_field='currency_id',
        store=False  
    )

    @api.depends('old_asset_original_value', 'additions_disposals')
    def _compute_close_asset_value(self):
        for asset in self:
            asset.close_asset_value = asset.old_asset_original_value + asset.additions_disposals-asset.disposal
            # asset.close_asset_value = asset.old_asset_original_value + asset.additions_disposals
            if asset.gross_increase_value:
                asset.close_asset_value+=asset.gross_increase_value

            asset.wdv = asset.close_asset_value - asset.closing_accumulated_depreciation

    @api.depends('original_move_line_ids','journal_entry')
    def _compute_additions_disposals(self):
        today = datetime.today().date()  # Ensure today's date is a date object
        if today.month >= 7:
            fiscal_year_start = datetime(today.year, 7, 1).date()
            fiscal_year_end = datetime(today.year + 1, 6, 30).date()
        else:
            fiscal_year_start = datetime(today.year - 1, 7, 1).date()
            fiscal_year_end = datetime(today.year, 6, 30).date()

        for asset in self:
            if asset.acquisition_date and fiscal_year_start <= asset.acquisition_date <= fiscal_year_end:
                if asset.state == 'open':
                    asset.additions_disposals = asset.original_value
                elif asset.state == 'close':
                    asset.additions_disposals = -asset.original_value
                else:
                    asset.additions_disposals = 0.0
            else:
                asset.additions_disposals = 0.0
            value=0
            value+=sum(asset.original_move_line_ids.mapped('debit'))
            value+=sum(asset.journal_entry.mapped('amount_total_signed'))
            asset.additions_disposals+=value






    # @api.depends('old_asset_original_value')
    # def _compute_disposal(self):
    #     for asset in self:
    #         asset.disposal =  -(asset.old_asset_original_value)







    # Compute methods
    @api.depends('sr_no')
    def _compute_opening_accumulated_depreciation(self):
        for asset in self:
            value = asset.old_asset_original_value - asset.original_value
            asset.opening_accumulated_depreciation = max(0, value)


    # @api.depends('depreciation_line_ids')
    # def _compute_depreciation_for_the_period(self):
    #     for asset in self:
    #         # Sum up all posted depreciation entries for the current asset
    #         asset.depreciation_for_the_period = sum(line.amount for line in asset.depreciation_line_ids.filtered(lambda l: l.move_check))

    @api.depends('opening_accumulated_depreciation', 'depreciation_for_the_period')
    def _compute_closing_accumulated_depreciation(self):
        for asset in self:
            asset.closing_accumulated_depreciation = asset.opening_accumulated_depreciation + asset.depreciation_for_the_period - asset.depreciation_disposal
            # asset.closing_accumulated_depreciation = asset.opening_accumulated_depreciation + asset.depreciation_for_the_period

    @api.depends('old_asset_original_value', 'closing_accumulated_depreciation')
    def _compute_wdv(self):
        for asset in self:
            asset.wdv = asset.old_asset_original_value - asset.closing_accumulated_depreciation
            if asset.state == 'close':
                asset.wdv = 0

    
    def get_largest_sr_no(self, data):
        # Initialize a variable to track the largest sr_no
        largest_sr_no = None
        
        # Iterate over the data once, checking for 'sr_no' and updating the largest value
        for item in data:
            if 'sr_no' in item:
                if largest_sr_no is None or item['sr_no'] > largest_sr_no:
                    largest_sr_no = item['sr_no']
        
        return largest_sr_no


    def validate(self):
        fields = [
            'method',
            'method_number',
            'method_period',
            'method_progress_factor',
            'salvage_value',
            'original_move_line_ids',
        ]
        ref_tracked_fields = self.env['account.asset'].fields_get(fields)
        self.write({'state': 'open'})
        
        # Fetch total number of active assets to compute next sr_no
        
        for asset in self:
            # Compute sr_no based on the current count of assets
            total_assets = asset.env['account.asset'].search([])
            # max_sr_no = asset.env['account.asset'].search([], order='sr_no desc', limit=1).sr_no

            max_sr_no = self.get_largest_sr_no(total_assets)
            
            # raise UserError(max_sr_no)
            asset.sr_no = max_sr_no + 1
            # total_assets += 1  # Increment for next record in case of multiple assets being validated
            
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del tracked_fields['method_progress_factor']
            
            dummy, tracking_value_ids = asset._mail_track(tracked_fields, dict.fromkeys(fields))
            asset_name = {
                'purchase': (_('Asset created'), _('An asset has been created for this move:')),
                'sale': (_('Deferred revenue created'), _('A deferred revenue has been created for this move:')),
                'expense': (_('Deferred expense created'), _('A deferred expense has been created for this move:')),
            }[asset.asset_type]
            msg = asset_name[1] + f' {asset._get_html_link()}'
            asset.message_post(body=asset_name[0], tracking_value_ids=tracking_value_ids)
            
            for move_id in asset.original_move_line_ids.mapped('move_id'):
                move_id.message_post(body=msg)
            
            if not asset.depreciation_move_ids:
                asset.compute_depreciation_board()
            
            asset._check_depreciations()
            asset.depreciation_move_ids.filtered(lambda move: move.state != 'posted')._post()
            
            if asset.account_asset_id.create_asset == 'no':
                asset._post_non_deductible_tax_value()



from odoo import models, fields

class AccountAssetDepreciationLine(models.Model):
    _name = 'account.asset.depreciation.line'
    _description = 'Asset Depreciation Line'

    asset_id = fields.Many2one('account.asset', string='Asset', ondelete='cascade')
    amount = fields.Float(string='Depreciation Amount')
    move_check = fields.Boolean(string='Posted', default=False)





class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'


    def sell_dispose(self):

        self.ensure_one()
        result = super().sell_dispose()
        if self.asset_id and self.modify_action =='sell':
            self.asset_id.disposal = -self.asset_id.old_asset_original_value
        else:
            self.asset_id.disposal = self.asset_id.old_asset_original_value
            self.asset_id.depreciation_disposal = self.asset_id.old_asset_original_value
        return result