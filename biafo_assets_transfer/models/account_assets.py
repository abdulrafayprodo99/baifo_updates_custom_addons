from odoo import fields, models, api, _



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