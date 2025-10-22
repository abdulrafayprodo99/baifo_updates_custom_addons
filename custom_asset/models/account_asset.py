from odoo import models, api

class AccountAssetCustom(models.Model):
    _inherit = "account.asset"

    @api.constrains('depreciation_move_ids')
    def _check_depreciations(self):
        for asset in self:
            if (
                asset.state == 'open'
                and asset.depreciation_move_ids
                and not asset.currency_id.is_zero(
                    asset.depreciation_move_ids.sorted(lambda x: (x.date, x.id))[-1].asset_remaining_value
                )
            ):
                # UserError removed
                pass
