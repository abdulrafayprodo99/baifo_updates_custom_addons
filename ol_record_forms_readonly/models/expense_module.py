from odoo import models, fields
from odoo.exceptions import UserError, ValidationError

class ExpenseModule(models.Model):
    _inherit = "expense.module"

    expense_module_readonly_check = fields.Boolean(string="Vendor Bills Readonly Check", compute="_compute_expense_module_readonly_check")

    def server_post_expense_action(self):             #Previous
        if self.state != 'posted':
            for rec in self:
                rec.expense_module_readonly_check = True
        super(ExpenseModule, self).server_post_expense_action()


    def _compute_expense_module_readonly_check(self):           #Aneeq Task Id: 43,871
            for rec in self:
                if rec.state == 'posted' and rec.approval_state_expense == 'approve':
                        rec.expense_module_readonly_check = True
                else:
                    rec.expense_module_readonly_check = False


    # def server_post_expense_action(self):             
        
    #     if self.state != 'posted' and self.approval_state_expense == False:
    #         for rec in self:
    #             rec.expense_module_readonly_check = False
    #     super(ExpenseModule, self).server_post_expense_action()

    # def button_draft(self):
    #     # super
    #     if self.move_type in ['in_invoice', 'out_invoice', 'entry'] and self.state == 'posted':
    #         for rec in self:
    #             rec.expense_module_readonly_check = False
    #     super(ExpenseModule, self).button_draft()