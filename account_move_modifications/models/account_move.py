from odoo import models,fields,api
from odoo.exceptions import UserError
from collections import defaultdict
from datetime import datetime
from datetime import date

class AccountMoveModifications(models.Model):
    _inherit="account.move"

    def getGroupedAccountJournals(self):
        self.ensure_one()
        filtered_dict = {} 
        for line in self.line_ids:
            account_name = line.account_id.name_get()[0][1] if len(line.account_id.name_get()) > 0 else ''
            if account_name not in filtered_dict:
                filtered_dict[account_name] = {
                    "account_id.name": account_name,
                    "name": line.name,
                    "analytic_distribution": f"{str(self.partner_id.name)  if self.partner_id else ''} {'-' if len(self._compute_analytic_distribution_name(line.analytic_distribution)) else ''} {','.join(self._compute_analytic_distribution_name(line.analytic_distribution))}",
                    "credit": 0,
                    "debit": 0
                }
            filtered_dict[account_name]["credit"] += line.credit
            filtered_dict[account_name]["debit"] += line.debit

        return list(filtered_dict.values())

    def _compute_analytic_distribution_name(self,analytic_distribution):
        for rec in self:
            filtered_accounts = set()
            if isinstance(analytic_distribution,dict):
                for key,val in analytic_distribution.items():
                    analytic_account = rec.env['account.analytic.account'].browse(int(key))
                    if analytic_account:
                        filtered_accounts.add(f"{analytic_account.name}")
            return filtered_accounts

    def getAnalyticAccounts(self):
        for rec in self:
            filtered_accounts = set()
            for line in rec.invoice_line_ids:
                if isinstance(line.analytic_distribution,dict):
                    for key,val in line.analytic_distribution.items():
                        analytic_account = rec.env['account.analytic.account'].browse(int(key))
                        if analytic_account and analytic_account.partner_id:
                            filtered_accounts.add(f"{analytic_account.name}")
            return filtered_accounts





class StockLotModifications(models.Model):
    _inherit="stock.lot"

    # active = fields.Boolean(default=True, string='Active')

    @api.model
    def _get_next_serial(self, company, product):
        """Return the next serial number to be attributed to the product."""
        if product.tracking != "none":
            last_serial = self.env['stock.lot'].search(
                [('company_id', '=', company.id), ('product_id', '=', product.id)],
                limit=1, order='id DESC')
            if last_serial:
                return self.env['stock.lot'].generate_lot_names(last_serial.name, 2)[1]
        return False

class MrpProductionInherited(models.Model):
    _inherit="mrp.production"


    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', readonly=False,
        domain=False,check_company=False, compute=False, store=True, precompute=False,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")
    compute_bom_domain =  fields.Many2many("mrp.bom",compute="_compute_bom_domain",store=True)



    

    
    # @api.depends('product_id')
    # def _compute_bom_domain(self):
    #     for rec in self:
    #         if rec.product_id:
    #             boms = rec.env['mrp.bom'].search([
    #                 ('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id),
    #                 ('company_id', '=', rec.env.company.id),
    #             ])
    #             rec.compute_bom_domain = [(6, 0, boms.ids)]  # Use (6, 0, ids) for Many2many

    #             # Reset bom_id if it doesn't belong to the new product
    #             if rec.bom_id and rec.bom_id not in boms:

    #                 rec.bom_id = False
                
    #             # Assign the first BOM if available
    #             if not rec.bom_id and boms:
    #                 raise UserError(str("Working"))
    #                 rec.bom_id = boms[0].id
    #         else:
    #             rec.compute_bom_domain = False
    #             rec.bom_id = False  # Clear bom_id if no product selected



    @api.onchange('product_id')
    def _onchange_product_id(self):
        today = date.today()
        for rec in self:
            domain = {'bom_id': []}
            if rec.product_id:
                boms = rec.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id),
                    ('company_id', '=', rec.env.company.id),
                    # M Azeem added below three filters
                    ('state','=','approved'),
                    ('effective_date', '<=', today),
                    ('end_date','>=',today),
                ])
                domain = {'bom_id': [('id', 'in', boms.ids)]}

                # Auto-select first BOM if none selected
                if not rec.bom_id and boms:
                    rec.bom_id = boms[0]
                elif rec.bom_id and rec.bom_id not in boms:
                    rec.bom_id = False

            return {'domain': domain}









    def _prepare_stock_lot_values(self):
        res = super(MrpProductionInherited, self)._prepare_stock_lot_values()

        self.ensure_one()
        
        current_datetime = datetime.now()
        current_fiscal_year = current_datetime.year
        
        # Check if it's a new fiscal year
        if self.product_id.tracking == 'lot':
            # Check if we need to reset the sequence
            if self.product_id.last_reset_year != current_fiscal_year:
                self.product_id.write({
                    'next_seq_number': 1,
                    'last_reset_year': current_fiscal_year
                })
            else:
                self.product_id.update_number_next()
            
            # Generate the lot name
            res['name'] = (
                f"{self.product_id.default_code}-"
                f"{current_datetime.strftime('%d%m%y')}-"
                f"{str(self.product_id.next_seq_number).rjust(4, '0')}"
            )

            exist_lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
                ('name', '=', res['name']),
            ], limit=1)
            if exist_lot:
                res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
                    
        else:
            res['name'] = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)        
        return {
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': res['name'],
        }

    def action_generate_serial(self):
        self.ensure_one()
        lot_values = self._prepare_stock_lot_values()
        
        last_lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
            ],order='id desc',limit=1)
        if last_lot:
            try:
                month=last_lot.name.split('-')[5][2:4]
                if int(month)<=6 and int(datetime.now().month) >6:
                    last_seq=0
                else:
                    last_seq = int(last_lot.name.split('-')[-1]) if len(last_lot.name.split('-')) > 0 else 0
            except Exception:
                last_seq = 0
            lot_values['name'] = (
                f"{self.product_id.default_code}-"
                f"{datetime.now().strftime('%d%m%y')}-"
                f"{str(last_seq+1).rjust(4, '0')}"
            )
        else:
            lot_values['name'] = (
                f"{self.product_id.default_code}-"
                f"{datetime.now().strftime('%d%m%y')}-"
                f"{str(1).rjust(4, '0')}"
            )
            self.product_id.next_seq_number = 1
        self.lot_producing_id = self.env['stock.lot'].create(lot_values)
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()


# Inherit mrp.production
from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    component_move_line_ids = fields.One2many(
        'stock.move.line',
        'move_id',
        string="Component Move Lines",
        compute='_compute_component_move_lines',
        store=True,
        readonly=False,
    )

    @api.depends('move_raw_ids.move_line_ids')
    def _compute_component_move_lines(self):
        for production in self:
            lines = production.move_raw_ids.mapped('move_line_ids')
            # production.component_move_line_ids = lines
    


    manual_move_line_ids = fields.One2many(
        'stock.move.line',
        'production_id',
        string="Detailed Component Operations"
    )
