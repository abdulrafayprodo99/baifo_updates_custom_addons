# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    product_uom_backup=fields.Many2one('uom.uom',compute="_compute_backup")

    @api.depends('product_uom_id')
    def _compute_backup(self):
        for rec in self:
            rec.product_uom_backup=rec.product_uom_id.id

class AccountMove(models.Model):
    _inherit = 'account.move'

    journal_type=fields.Char("Journal Type",compute="_compute_type")
    asset=fields.Many2many(comodel_name='account.asset',string="Tag Asset")

    def _compute_type(self):
        for rec in self:
            rec.journal_type=rec.journal_id.type

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        for move in self:
            if move.asset:
                move.asset.journal_entry = move.id

class AccountAsset(models.Model):
    _inherit = 'account.asset'
    journal_entry = fields.Many2many(comodel_name='account.move', string="Journal Entry", readonly=False)    

    @api.onchange('journal_entry_id')
    def _onchange_asset_id(self):
        for asset in self:
            if asset.journal_entry:
                asset.journal_entry.asset = asset.id