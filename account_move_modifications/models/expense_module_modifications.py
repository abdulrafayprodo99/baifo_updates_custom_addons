from odoo import models,api,fields
from odoo.exceptions import UserError

class ExpenseModuleModifications(models.Model):
    _inherit="expense.module"

    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        landed_costs_lines = self.expense_line.filtered(lambda line: line.is_landed_costs_line)
        landed_costs = self.env['stock.landed.cost'].create({
            'expense_bill_id': self.id,
            'partner': landed_costs_lines[0].partner.id,
            'analytical_field': landed_costs_lines[0].analytical_field,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.property_account_expense_id.id,
                'price_unit': self.env.company.currency_id._convert(l.value, self.env.company.currency_id, self.env.company, l.expense_module_id.date),
                'split_method': l.product_id.split_method_landed_cost or 'equal',
                'analytic_distribution_landed_cost':l.analytical_field
            }) for l in landed_costs_lines],
        })
        # action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        # return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])
        return True



class LandedCostsModifications(models.Model):
    _inherit="stock.landed.cost"

    partner = fields.Many2one(string="Partner",comodel_name="res.partner")
    analytical_field =fields.Json(string="Analytical Field",default="{}")
    analytic_precision = fields.Integer(string='Analytic Precision')
    analytical_field_name =  fields.Char(string="Analytical Field Name", compute="_compute_analytical_field_name",store=True)
    @api.depends('analytical_field')
    def _compute_analytical_field_name(self):
        for rec in self:
            if isinstance(rec.analytical_field,dict):
                analytic_account = rec.env['account.analytic.account'].browse(int(list(rec.analytical_field.keys())[0])) if len(list(rec.analytical_field.keys())) > 0 else ''
                rec.analytical_field_name = f"{analytic_account.name}-{analytic_account.partner_id.name if analytic_account.partner_id else ''}"  if analytic_account else ''
            else:
                rec.analytical_field_name = ''
    

    def approve_landed_cost_approval(self):
        for rec in self:
            for picking in rec.picking_ids:
                to_approve =  rec.env['landed.cost.apporoval'].search(['&',('grn_no','=',picking.id),('approval_state','!=','approve')])
                if to_approve:
                    if to_approve.approval_state == 'verify':
                        to_approve.action_approve()
                    elif to_approve.approval_state == 'prepared':
                        to_approve.action_verify()
                        to_approve.action_approve()
                    else:
                        to_approve.action_prepared()
                        to_approve.action_verify()
                        to_approve.action_approve()