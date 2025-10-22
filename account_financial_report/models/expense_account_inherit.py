from odoo import models, fields

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    expense_id = fields.Many2one('expense.module', string='Expense Record')



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    memo = fields.Text(string='Memo', compute='_compute_memo')

    # account_tag_ids = fields.Many2many('account.account.tag',string='Tags',help='Tags are used to classify entries for reporting purpose.')
    # related='account_id.tag_ids',
    # store = True,

    # tax_tag_ids = fields.Many2many(
    #     string="Tags",
    #     comodel_name='account.account.tag',
    #     related='account_id.tag_ids',
    #     ondelete='restrict',
    #     context={'active_test': False},
    #     tracking=True,
    #     help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.",
    # )

    @api.depends('move_id.expense_id')
    def _compute_memo(self):
        for line in self:
            # Fetch the related expense module's memo field
            line.memo = line.move_id.expense_id.memo if line.move_id.expense_id else ''
            # raise UserError(str(line.move_id.expense_id.memo))