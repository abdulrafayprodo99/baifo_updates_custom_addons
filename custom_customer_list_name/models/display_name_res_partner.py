from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name')
    def _compute_display_name(self):
        # Use the same logic as the base implementation
        names = dict(self.with_context({}).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

            raise UserError(partner.display_name)

    display_name = fields.Char(compute='_compute_display_name', recursive=True,  index=True)