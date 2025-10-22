from odoo import models, fields, api

class TrialBalanceReportWizard(models.TransientModel):
    _inherit = 'trial.balance.report.wizard'
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')
