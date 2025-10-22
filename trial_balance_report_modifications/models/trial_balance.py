from odoo import models,fields,api,_
from odoo.exceptions import UserError

class TrialBalance(models.AbstractModel):
    _inherit = 'report.account_financial_report.trial_balance'

    @api.model
    def _compute_partner_amount(
        self, total_amount, tb_initial_prt, tb_period_prt, foreign_currency
    ):
        partners_ids = set()
        partners_data = {}
        for tb in tb_period_prt:
            acc_id = tb["account_id"][0]
            prt_id = tb["partner_id"][0] if tb["partner_id"] else 0
            if prt_id not in partners_ids:
                partner_name = (
                    tb["partner_id"][1] if tb["partner_id"] else _("Missing Partner")
                )
                partner_obj = self.env["res.partner"].browse(int(prt_id))
                
                partners_data.update({prt_id: {"id": prt_id, "name": partner_name,"code":partner_obj.x_studio_new_code if partner_obj else ""}})
                

            total_amount[acc_id][prt_id] = self._prepare_total_amount(
                tb, foreign_currency
            )
            total_amount[acc_id][prt_id]["credit"] = tb["credit"]
            total_amount[acc_id][prt_id]["debit"] = tb["debit"]
            total_amount[acc_id][prt_id]["balance"] = tb["balance"]
            total_amount[acc_id][prt_id]["initial_balance"] = 0.0
            partners_ids.add(prt_id)
        for tb in tb_initial_prt:
            acc_id = tb["account_id"][0]
            prt_id = tb["partner_id"][0] if tb["partner_id"] else 0
            if prt_id not in partners_ids:
                partner_name = (
                    tb["partner_id"][1] if tb["partner_id"] else _("Missing Partner")
                )
                partner_obj = self.env["res.partner"].browse(int(prt_id))
                partners_data.update({prt_id: {"id": prt_id, "name": partner_name,"code":partner_obj.x_studio_new_code if partner_obj else ""}})

            total_amount = self._compute_acc_prt_amount(
                total_amount, tb, acc_id, prt_id, foreign_currency
            )
        # sorted_keys = sorted(partners_data.keys(), key=lambda x: str(partners_data[x].get('code', '')))
        # partners_data = {k: partners_data[k] for k in sorted_keys if k in partners_data.keys()}
        # total_amount = {k: total_amount[k] for k in sorted_keys if k in total_amount.keys()}
        
        return total_amount, partners_data

    
    def _get_report_values(self, docids, data):
        show_partner_details = data["show_partner_details"]
        wizard_id = data["wizard_id"]
        trial_balance_wizard = self.env["trial.balance.report.wizard"].browse(int(wizard_id))
        analytic_account_ids = trial_balance_wizard.analytic_account_ids

        company     = self.env["res.company"].browse(data["company_id"])
        company_id  = data["company_id"]
        partner_ids = data["partner_ids"]
        journal_ids = data["journal_ids"]
        account_ids = data["account_ids"]
        date_to     = data["date_to"]
        date_from   = data["date_from"]
        hide_account_at_0 = data["hide_account_at_0"]
        show_hierarchy = data["show_hierarchy"]
        show_hierarchy_level = data["show_hierarchy_level"]
        foreign_currency = data["foreign_currency"]
        only_posted_moves = data["only_posted_moves"]
        unaffected_earnings_account = data["unaffected_earnings_account"]
        fy_start_date = data["fy_start_date"]
        total_amount, accounts_data, partners_data = self._get_data(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_to,
            date_from,
            foreign_currency,
            only_posted_moves,
            show_partner_details,
            hide_account_at_0,
            unaffected_earnings_account,
            fy_start_date,
            analytic_account_ids,
            wizard_id
        )
        trial_balance = []
        if not show_partner_details:
            for account_id in accounts_data.keys():
                accounts_data[account_id].update(
                    {
                        "initial_balance": total_amount[account_id]["initial_balance"],
                        "credit": total_amount[account_id]["credit"],
                        "debit": total_amount[account_id]["debit"],
                        "balance": total_amount[account_id]["balance"],
                        "ending_balance": total_amount[account_id]["ending_balance"],
                        "type": "account_type",
                    }
                )
                if foreign_currency:
                    accounts_data[account_id].update(
                        {
                            "ending_currency_balance": total_amount[account_id][
                                "ending_currency_balance"
                            ],
                            "initial_currency_balance": total_amount[account_id][
                                "initial_currency_balance"
                            ],
                        }
                    )
            if show_hierarchy:
                groups_data = self._get_groups_data(
                    accounts_data, total_amount, foreign_currency
                )
                trial_balance = list(groups_data.values())
                trial_balance += list(accounts_data.values())
                trial_balance = sorted(trial_balance, key=lambda k: k["complete_code"])
                for trial in trial_balance:
                    counter = trial["complete_code"].count("/")
                    trial["level"] = counter
            else:
                trial_balance = list(accounts_data.values())
                trial_balance = sorted(trial_balance, key=lambda k: k["code"])
        else:
            if foreign_currency:
                for account_id in accounts_data.keys():
                    total_amount[account_id]["currency_id"] = accounts_data[account_id][
                        "currency_id"
                    ]
                    total_amount[account_id]["currency_name"] = accounts_data[
                        account_id
                    ]["currency_name"]
        if show_partner_details:
            sorted_keys = sorted(partners_data.keys(), key=lambda x: str(partners_data[x].get('code', '')))

            partners_data = {k: partners_data[k] for k in sorted_keys if k in partners_data.keys()}
            final_total_amount ={}
            for key,val in total_amount.items():
                account_group = {}
                for i in sorted_keys:
                    for k,v in val.items():
                        if isinstance(k, int) and k == i:
                            account_group.update({k:v})
                        elif isinstance(k, str):
                            account_group.update({k:v})
                final_total_amount.update({key:account_group})
            
            total_amount = final_total_amount
        docs = self.env["trial.balance.report.wizard"].browse(wizard_id)
        show_analytic_account = False
        if docs.analytic_account_ids and not data["show_partner_details"]:
            show_analytic_account = True
        return {
            "doc_ids": [wizard_id],
            "doc_model": "trial.balance.report.wizard",
            "docs":docs ,
            "show_analytic_account": show_analytic_account,
            "foreign_currency": data["foreign_currency"],
            "company_name": company.display_name,
            "company_currency": company.currency_id,
            "currency_name": company.currency_id.name,
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "only_posted_moves": data["only_posted_moves"],
            "hide_account_at_0": data["hide_account_at_0"],
            "show_partner_details": data["show_partner_details"],
            "limit_hierarchy_level": data["limit_hierarchy_level"],
            "show_hierarchy": show_hierarchy,
            "hide_parent_hierarchy_level": data["hide_parent_hierarchy_level"],
            "trial_balance": trial_balance,
            "total_amount": total_amount,
            "accounts_data": accounts_data,
            "partners_data": partners_data,
            "show_hierarchy_level": show_hierarchy_level,
            "currency_model": self.env["res.currency"],
        }


    
    @api.model
    def _get_data(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        date_to,
        date_from,
        foreign_currency,
        only_posted_moves,
        show_partner_details,
        hide_account_at_0,
        unaffected_earnings_account,
        fy_start_date,
        analytic_account_ids=0,
        wizard_id=0
    ):
        accounts_domain = [("company_id", "=", company_id)]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]
            # If explicit list of accounts is provided,
            # don't include unaffected earnings account
            unaffected_earnings_account = False
        accounts = self.env["account.account"].search(accounts_domain)
        tb_initial_acc = []
        for account in accounts:
            tb_initial_acc.append(
                {"account_id": account.id, "balance": 0.0, "amount_currency": 0.0}
            )
        initial_domain_bs = self._get_initial_balances_bs_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        tb_initial_acc_bs = self.env["account.move.line"].read_group(
            domain=initial_domain_bs,
            fields=["account_id", "balance", "amount_currency:sum"],
            groupby=["account_id"],
        )
        initial_domain_pl = self._get_initial_balances_pl_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_from,
            only_posted_moves,
            show_partner_details,
            fy_start_date,
        )
        tb_initial_acc_pl = self.env["account.move.line"].read_group(
            domain=initial_domain_pl,
            fields=["account_id", "balance", "amount_currency:sum"],
            groupby=["account_id"],
        )
        tb_initial_acc_rg = tb_initial_acc_bs + tb_initial_acc_pl
        for account_rg in tb_initial_acc_rg:
            element = list(
                filter(
                    lambda acc_dict: acc_dict["account_id"]
                    == account_rg["account_id"][0],
                    tb_initial_acc,
                )
            )
            if element:
                element[0]["balance"] += account_rg["balance"]
                element[0]["amount_currency"] += account_rg["amount_currency"]
        if hide_account_at_0:
            tb_initial_acc = [p for p in tb_initial_acc if p["balance"] != 0]

        period_domain = self._get_period_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_to,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        tb_period_acc = self.env["account.move.line"].read_group(
            domain=period_domain,
            fields=["account_id", "debit", "credit", "balance", "amount_currency:sum"],
            groupby=["account_id"],
        )

        if show_partner_details:
            tb_initial_prt_bs = self.env["account.move.line"].read_group(
                domain=initial_domain_bs,
                fields=["account_id", "partner_id", "balance", "amount_currency:sum"],
                groupby=["account_id", "partner_id"],
                lazy=False,
            )
            tb_initial_prt_pl = self.env["account.move.line"].read_group(
                domain=initial_domain_pl,
                fields=["account_id", "partner_id", "balance", "amount_currency:sum"],
                groupby=["account_id", "partner_id"],
            )
            tb_initial_prt = tb_initial_prt_bs + tb_initial_prt_pl
            if hide_account_at_0:
                tb_initial_prt = [p for p in tb_initial_prt if p["balance"] != 0]
            tb_period_prt = self.env["account.move.line"].read_group(
                domain=period_domain,
                fields=[
                    "account_id",
                    "partner_id",
                    "debit",
                    "credit",
                    "balance",
                    "amount_currency:sum",
                ],
                groupby=["account_id", "partner_id"],
                lazy=False,
            )
        total_amount = {}
        partners_data = []
        total_amount = self._compute_account_amount(
            total_amount, tb_initial_acc, tb_period_acc, foreign_currency
        )
        if show_partner_details:
            total_amount, partners_data = self._compute_partner_amount(
                total_amount, tb_initial_prt, tb_period_prt, foreign_currency
            )
        # Remove accounts a 0 from collections
        if hide_account_at_0:
            company = self.env["res.company"].browse(company_id)
            self._remove_accounts_at_cero(total_amount, show_partner_details, company)

        accounts_ids = list(total_amount.keys())
        unaffected_id = unaffected_earnings_account
        if unaffected_id:
            if unaffected_id not in accounts_ids:
                accounts_ids.append(unaffected_id)
                total_amount[unaffected_id] = {}
                total_amount[unaffected_id]["initial_balance"] = 0.0
                total_amount[unaffected_id]["balance"] = 0.0
                total_amount[unaffected_id]["credit"] = 0.0
                total_amount[unaffected_id]["debit"] = 0.0
                total_amount[unaffected_id]["ending_balance"] = 0.0
                if foreign_currency:
                    total_amount[unaffected_id]["initial_currency_balance"] = 0.0
                    total_amount[unaffected_id]["ending_currency_balance"] = 0.0
        accounts_data = self._get_accounts_data_(accounts_ids,wizard_id)
        # raise UserError(str(accounts_data)) # Rao
        (
            pl_initial_balance,
            pl_initial_currency_balance,
        ) = self._get_pl_initial_balance(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            fy_start_date,
            only_posted_moves,
            show_partner_details,
            foreign_currency,
        )
        if unaffected_id:
            total_amount[unaffected_id]["ending_balance"] += pl_initial_balance
            total_amount[unaffected_id]["initial_balance"] += pl_initial_balance
            if foreign_currency:
                total_amount[unaffected_id][
                    "ending_currency_balance"
                ] += pl_initial_currency_balance
                total_amount[unaffected_id][
                    "initial_currency_balance"
                ] += pl_initial_currency_balance
        return total_amount, accounts_data, partners_data

    
    def _get_accounts_data_(self, accounts_ids,wizard_id):
        accounts = self.env["account.account"].browse(accounts_ids)
        wizard_data =  self.env["trial.balance.report.wizard"].browse(wizard_id)
        accounts_data = {}
        for account in accounts:
            analytics_data_wrt_account = {}
            if wizard_data and wizard_data.analytic_account_ids:
                for analytic_account in wizard_data.analytic_account_ids:
                    account_move_lines =  self.env['account.move.line'].search([('parent_state', '=', 'posted'),('account_id', '=', account.id),('analytic_account_ids', '=', analytic_account.id)])
                    if account_move_lines:
                        lines_period = account_move_lines.filtered(lambda line: line.date <= wizard_data.date_to and line.date >= wizard_data.date_from)
                        debit = sum(map(lambda x: x.debit,lines_period))
                        credit= sum(map(lambda x: x.credit,lines_period))
                        period_balance = debit - credit
                        lines_initial = account_move_lines.filtered(lambda line: line.date < wizard_data.date_from)
                        initial_balance = sum(map(lambda x: x.balance,lines_initial))
                        # lines_ending = account_move_lines.filtered(lambda line: line.date > wizard_data.date_to)
                        ending_balance = initial_balance + (debit - credit)
                        analytics_data_wrt_account.update({analytic_account.id: {'code':analytic_account.code,'name':analytic_account.name, 'debit':debit, 'credit':credit,'initial_balance':initial_balance,'ending_balance':ending_balance,'balance':period_balance}})
            
            accounts_data.update(
                {
                    account.id: {
                        "id": account.id,
                        "code": account.code,
                        "name": account.name,
                        # Uzair Ahmed
                        # Add the analytic account to the data
                        "analytic_accounts": list(analytics_data_wrt_account.values()),
                        "hide_account": False,
                        "group_id": account.group_id.id,
                        "currency_id": account.currency_id.id,
                        "currency_name": account.currency_id.name,
                        "centralized": account.centralized,
                    }
                }
            )
        return accounts_data