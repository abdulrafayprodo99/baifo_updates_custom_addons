from collections import defaultdict
from odoo import api, fields, models, Command, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import  float_compare

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account", compute="_compute_analytic_account_ids", store=True
    )

    def write(self,vals):
        res=super(AccountMoveLine, self).write(vals)
        for rec in self:
            if isinstance(vals,dict) and not vals.get('date') and not rec.date and rec.move_id.date:
                rec.write({'date':rec.move_id.date})
            if isinstance(vals,dict) and not vals.get('analytic_account_ids') and not rec.analytic_account_ids and rec.analytic_distribution:
                rec._compute_analytic_account_ids()
        return res

    @api.depends("analytic_distribution")
    def _compute_analytic_account_ids(self):
        # Prefetch all involved analytic accounts
        with_distribution = self.filtered("analytic_distribution")
        batch_by_analytic_account = defaultdict(list)
        for record in with_distribution:
            for account_id in map(int, record.analytic_distribution):
                batch_by_analytic_account[account_id].append(record.id)
        existing_account_ids = set(
            self.env["account.analytic.account"]
            .browse(map(int, batch_by_analytic_account))
            .exists()
            .ids
        )
        # Store them
        self.analytic_account_ids = False
        for account_id, record_ids in batch_by_analytic_account.items():
            if account_id not in existing_account_ids:
                continue
            self.browse(record_ids).analytic_account_ids = [
                fields.Command.link(account_id)
            ]

    def init(self):
        """
            The join between accounts_partners subquery and account_move_line
            can be heavy to compute on big databases.
            Join sample:
                JOIN
                    account_move_line ml
                        ON ap.account_id = ml.account_id
                        AND ml.date < '2018-12-30'
                        AND ap.partner_id = ml.partner_id
                        AND ap.include_initial_balance = TRUE
            By adding the following index, performances are strongly increased.
        :return:
        """
        self._cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = " "%s",
            ("account_move_line_account_id_partner_id_index",),
        )
        if not self._cr.fetchone():
            self._cr.execute(
                """
            CREATE INDEX account_move_line_account_id_partner_id_index
            ON account_move_line (account_id, partner_id)"""
            )

    @api.model
    def search_count(self, domain, limit=None):
        # In Big DataBase every time you change the domain widget this method
        # takes a lot of time. This improves performance
        if self.env.context.get("skip_search_count"):
            return 0
        return super().search_count(domain, limit=limit)

    def _create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic distribution.
        """
        self._validate_analytic_distribution()
        analytic_line_vals = []
        for line in self:
            analytic_line_vals.extend(line._prepare_analytic_lines())
        # raise UserError(str(analytic_line_vals))
        self.env['account.analytic.line'].create(analytic_line_vals)

    
    def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        self.ensure_one()
        account_id = int(account_id)
        account = self.env['account.analytic.account'].browse(account_id)
        distribution_plan = distribution_on_each_plan.get(account.root_plan_id, 0) + distribution
        decimal_precision = self.env['decimal.precision'].precision_get('Percentage Analytic')
        if float_compare(distribution_plan, 100, precision_digits=decimal_precision) == 0:
            amount = -self.balance * (100 - distribution_on_each_plan.get(account.root_plan_id, 0)) / 100.0
        else:
            amount = -self.balance * distribution / 100.0
        distribution_on_each_plan[account.root_plan_id] = distribution_plan
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        return {
            'name': default_name,
            'date': self.date or self.move_id.date or False,
            'account_id': account_id,
            'partner_id': self.partner_id.id,
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_line_id': self.id,
            'user_id': self.move_id.invoice_user_id.id or self._uid,
            'company_id': account.company_id.id or self.company_id.id or self.env.company.id,
            'category': 'invoice' if self.move_id.is_sale_document() else 'vendor_bill' if self.move_id.is_purchase_document() else 'other',
        }