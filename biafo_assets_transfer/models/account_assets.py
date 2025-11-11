from odoo import fields, models, api, _
from math import copysign



class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def action_asset_modify(self):
        """ Returns an action opening the asset modification wizard.
        """
        self.ensure_one()
        new_wizard = self.env['asset.modify'].create({
            'asset_id': self.id,
            'modify_action': 'resume' if self.env.context.get(
                'resume_after_pause') else 'dispose' if self.asset_type == 'purchase' else 'modify',
        })
        return {
            'name': _('Modify Asset'),
            'view_mode': 'form',
            'res_model': 'asset.modify',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
            'context': {
                'active_id': self.id,
                'active_model': self._name,
            }
        }



    def _get_transfer_moves(self, invoice_lines_list, disposal_date,fixed_asset_account,dep_asset_account,asset_name):
        """Create the move for the disposal of an asset.

        :param invoice_lines_list: list of recordset of `account.move.line`
            Each element of the list corresponds to one record of `self`
            These lines are used to generate the disposal move
        :param disposal_date: the date of the disposal
        """

        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'balance': -amount,
                'analytic_distribution': analytic_distribution,
                'currency_id': asset.currency_id.id,
                'amount_currency': -asset.company_id.currency_id._convert(
                    from_amount=amount,
                    to_currency=asset.currency_id,
                    company=asset.company_id,
                    date=disposal_date,
                )
            })

        move_ids = []
        assert len(self) == len(invoice_lines_list)
        for asset, invoice_line_ids in zip(self, invoice_lines_list):
            asset._create_move_before_date(disposal_date)

            analytic_distribution = asset.analytic_distribution

            dict_invoice = {}
            invoice_amount = 0

            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(
                asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id

            all_lines_before_disposal = asset.depreciation_move_ids.filtered(lambda x: x.date <= disposal_date)
            depreciated_amount = asset.currency_id.round(copysign(
                sum(all_lines_before_disposal.mapped(
                    'depreciation_value')) + asset.already_depreciated_amount_import,
                -initial_amount,
            ))
            depreciation_account = asset.account_depreciation_id
            for invoice_line in invoice_line_ids:
                dict_invoice[invoice_line.account_id] = copysign(invoice_line.balance,
                                                                 -initial_amount) + dict_invoice.get(
                    invoice_line.account_id, 0)
                invoice_amount += copysign(invoice_line.balance, -initial_amount)
            list_accounts = [(amount, account) for account, amount in dict_invoice.items()]
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = fixed_asset_account
            line_datas = [(initial_amount, initial_account),
                          (depreciated_amount, depreciation_account)] + list_accounts + [
                             (difference, difference_account)]
            vals = {
                'asset_id': asset.id,
                'ref': asset_name,
                'asset_depreciation_beginning_date': disposal_date,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'move_type': 'entry',
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            asset.write({'depreciation_move_ids': [(0, 0, vals)]})

            #2nd entry
            dep_on_disposal_amount = self.depreciation_disposal
            difference_disposal_current = abs(abs(depreciated_amount) -  dep_on_disposal_amount)

            line_datas2 = [(difference_disposal_current, initial_account),
                          (-difference_disposal_current, depreciation_account)] + list_accounts + [
                             (-dep_on_disposal_amount,fixed_asset_account),(dep_on_disposal_amount,dep_asset_account)]
            vals_2 = {
                'asset_id': asset.id,
                'ref': f'{asset_name} -Balanced Entry',
                'asset_depreciation_beginning_date': disposal_date,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'move_type': 'entry',
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas2 if account],
            }
            asset.write({'depreciation_move_ids': [(0, 0, vals_2)]})
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids
            account_moves = self.env['account.move'].browse(move_ids)
            posted_move_ids = []
            for account_move in account_moves:
                if not account_move.auto_post or account_move.auto_post == 'no':
                   account_move.action_post()
                   posted_move_ids.append(account_move.id)

        return posted_move_ids