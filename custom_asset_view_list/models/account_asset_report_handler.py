# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools import format_date
from itertools import groupby
from collections import defaultdict
from odoo.exceptions import UserError

class AssetReportCustomHandler(models.AbstractModel):
    _inherit = 'account.asset.report.handler'

    
    #
    # def _query_lines(self, options, prefix_to_match=None, forced_account_id=None):
    #     """
    #     Returns a list of tuples: [(asset_id, account_id, [{expression_label: value}])]
    #
    #
    #     """
    #
    #     lines=super(AssetReportCustomHandler,self)._query_lines(options,prefix_to_match,forced_account_id)
    #     for line in lines:
    #         asset_id=line[1]
    #         asset=self.env['account.asset'].search([('id','=',asset_id)])
    #         opening_accumulated_depreciation=asset.opening_accumulated_depreciation
    #         old_asset_original_value=asset.old_asset_original_value
    #         # line[2]['opening_accumulated_depreciation']=opening_accumulated_depreciation
    #         # line[2]['old_asset_original_value']=old_asset_original_value
    #         line[2]['assets_date_from']=asset.old_asset_original_value
    #         line[2]['assets_minus']=asset.disposal
    #         # line[2]['assets_date_to']=old_asset_original_value+asset.additions_disposals-asset.disposal
    #         # line[2]['assets_date_to']=old_asset_original_value+asset.original_value-asset.disposal
    #         line[2]['assets_date_to']=old_asset_original_value+line[2]['assets_plus']-asset.disposal
    #         line[2]['depre_date_from']=opening_accumulated_depreciation
    #         line[2]['depre_plus']=asset.depreciation_for_the_period
    #         line[2]['depre_minus']=asset.depreciation_disposal
    #         line[2]['depre_date_to']=asset.closing_accumulated_depreciation
    #         line[2]['balance']=line[2]['assets_date_to']-line[2]['depre_date_to']
    #     return lines

    def _query_lines(self, options, prefix_to_match=None, forced_account_id=None):
        """
        Optimized version: performs a single batch query for assets to avoid timeouts.
        Returns a list of tuples: [(asset_id, account_id, [{expression_label: value}])]
        """

        lines = super(AssetReportCustomHandler, self)._query_lines(options, prefix_to_match, forced_account_id)

        if not lines:
            return lines

        # ✅ Collect all asset_ids at once
        asset_ids = [line[1] for line in lines if line[1]]
        assets = self.env['account.asset'].browse(asset_ids)

        # ✅ Convert assets to dict for O(1) lookup
        assets_dict = {asset.id: asset for asset in assets}

        for line in lines:
            asset_id = line[1]
            asset = assets_dict.get(asset_id)
            if not asset:
                continue

            opening_accumulated_depreciation = asset.opening_accumulated_depreciation
            old_asset_original_value = asset.old_asset_original_value

            line[2]['assets_date_from'] = old_asset_original_value
            line[2]['assets_minus'] = asset.disposal
            line[2]['assets_date_to'] = old_asset_original_value + line[2].get('assets_plus', 0.0) - asset.disposal
            line[2]['depre_date_from'] = opening_accumulated_depreciation
            line[2]['depre_plus'] = asset.depreciation_for_the_period
            line[2]['depre_minus'] = asset.depreciation_disposal
            line[2]['depre_date_to'] = asset.closing_accumulated_depreciation
            line[2]['balance'] = line[2]['assets_date_to'] - line[2]['depre_date_to']

        return lines
