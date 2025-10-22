# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime


BANK_VOUCHER__STATES = [
   ('prepared','Prepared'),
   ('check','Checked'),
   ('verify','Verified'),
   ('audit','Audited'),
   ('approve','Approved'),
]

EXPENSE_STATES = [  
   ('prepared','Prepared'),
   ('verify','Verified'),
   ('approve','Approved'),
   
]

class RecordExpense(models.Model):
    _name = "expense.module"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Expense Module"

    name = fields.Char(string='Record Expense Reference', readonly=True,)
    payment_type = fields.Selection([('journal_voucher', 'Journal Voucher'), ('bank_payment', 'Bank Payment')], string='Payment Type', required=True) # Rao
    paid_to = fields.Char(string='Paid To' ,copy=True)
    journal = fields.Many2one('account.journal',string='Journal' ,copy=True)
    account_id = fields.Many2one('account.account',string='Account', copy=True)
    currency_id = fields.Many2one('res.currency',string='Currency',copy=True,  related='journal.company_id.currency_id',
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)
    memo = fields.Text(string='Memo', copy=True)
    is_posted = fields.Char(string='Is Posted' ,copy=True)
    posting_date = fields.Date(string='Posting Date',copy=True)
    date = fields.Date(string='Accounting Date')
    cheque_date = fields.Date(string='Cheque Date')
    cheque_number = fields.Char(string='Cheque Number',copy=True)
    total_expense = fields.Monetary(string='Total Expense',copy=True, compute = "compute_total_amount")
    is_bank_payment = fields.Selection([('no', 'No'),('yes', 'Yes')], string='Is Bank Payment', required=True)
    # expense_amount_in_words = fields.Char(string='Expense Amount In Words', readonly=True)
    expense_line = fields.One2many('expense.line', 'expense_module_id',copy=True ,string="Expense Line")
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string='Status')
    expense_count = fields.Integer(string='Journal Entry', compute='get_expense_count')
    analytical_field=fields.Json()
    analytic_precision = fields.Integer(string='Analytic Precision')
    
    total_credit = fields.Float(string='Total Credit',compute="compute_credit_debit",store=True,digits=(10, 2))
    total_debit = fields.Float(string='Total Debit',compute="compute_credit_debit",store=True,digits=(10, 2))
    # , compute="compute_credit_debit"
    # , compute="compute_credit_debit"
    # def amount_in_words(self):
    #     self.expense_amount_in_words = str(self.currency_id.amount_to_text(self.total_expense)) + ' only'


    
    landed_costs_visible = fields.Boolean(compute='_compute_landed_costs_visible')
    landed_costs_ids = fields.One2many('stock.landed.cost', 'expense_bill_id', string='Landed Costs')


    # Approvals Bank Payment
    
    approval_state = fields.Selection(selection=BANK_VOUCHER__STATES, string="Approval Status",copy=False,)

    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepare Timestamp" , readonly=True,copy=False)
    # checked_by = fields.Many2one("res.users", string="Checked by",copy=False)
    # checked_timestamp = fields.Datetime(strng="Check Timestamp" , readonly=True,copy=False)
    verify_by = fields.Many2one("res.users", string="Verify by",copy=False)
    verify_timestamp = fields.Datetime(strng="Verify Timestamp" , readonly=True,copy=False)
    # audit_by = fields.Many2one("res.users", string="Audited by",copy=False)
    # audit_timestamp = fields.Datetime(strng="Audit Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # readonly_check = fields.Boolean('Readonly Check',copy = False)

    # Rao Abdul Rehman

    lines_modified = fields.Boolean(string="Lines Modified", default=False, copy=False)

    @api.onchange('expense_line')
    def _onchange_expense_line(self):

        self.lines_modified = True

    def action_update_journal_entry(self):

        if self.state != 'posted':
            for rec in self:

                journal_entry = self.env['account.move'].search([('expense_id', '=', rec.id)])

                if journal_entry:

                    journal_entry.unlink()

                    lines = []
                    for rec1 in self:

                        credit = 0
                        for rec in rec1.expense_line:
                            if rec.general_item_type == 'debit':
                                line = (0, 0, {
                                    'account_id': rec.account.id,
                                    'debit': rec.value,
                                    'name':rec.description,
                                    'partner_id': rec.partner.id,
                                    'analytic_distribution': rec.analytical_field,
                                })
                                lines.append(line)
                            if rec.general_item_type == 'credit':     
                                credit = rec.value
                                line_ = (0, 0, {
                                    'account_id': rec.account.id,
                                    'credit': credit,
                                    'name':rec.description,
                                    'partner_id': rec.partner.id,
                                    'analytic_distribution': rec.analytical_field
                                    })
                                lines.append(line_)
                        
                        self.env['account.move'].with_context(check_move_validity=False).create({
                            'name':rec1.name,
                            'journal_id': rec1.journal.id,
                            'date': rec1.date,
                            'invoice_date': rec1.date,
                            'line_ids': lines,
                            'expense_id': rec1.id, 
                        })
                    
                    # Reset the flag after updating the journal entry
        
                    self.lines_modified = False

        else:
            raise UserError('This Document is already posted')

    
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        
        if self.payment_type == 'journal_voucher':
            self.journal = 3
            self.is_bank_payment = 'no'
        else:
            self.is_bank_payment = 'yes'
            return{
                'domain': {'journal': [('type', '=', 'bank')]}
            }
    
    
    # sherahmed
    seq_generate = fields.Boolean(string="Sequence Generated", default=False, copy=False)
    temp_name = fields.Char(string="Temporary Number")
    
    def create_expense_journal_entry(self):
        if (self.is_bank_payment == 'yes' and self.approval_state_expense == "prepared") or (self.is_bank_payment == 'no' and self.approval_state_expense == "prepared"):
        
            lines = []
            for rec1 in self:
                
                if rec1.state == 'posted':
                    raise UserError('This Document is already posted')
                else:
                    credit = 0
                    for rec in rec1.expense_line:
                        if rec.general_item_type == 'debit':
                            line = (0, 0, {
                                'account_id': rec.account.id,
                                'debit': rec.value,
                                'name':rec.description,
                                'partner_id': rec.partner.id,
                                'analytic_distribution': rec.analytical_field,
                                # 'analytic_tag_ids': rec.tags,
                            })
                            lines.append(line)
                        if rec.general_item_type == 'credit':     
                            credit = rec.value
                            line_ = (0, 0, {
                                # 'account_id': rec1.journal.default_account_id.id if rec1.journal.is_miscellaneous_journal else rec1.account_id.id ,
                                'account_id': rec.account.id,
                                'credit': credit,
                                'name':rec.description,
                                'partner_id': rec.partner.id,
                                'analytic_distribution': rec.analytical_field
                                })
                            lines.append(line_)
                    
                    self.env['account.move'].with_context(check_move_validity=False).create({
                        'name':rec1.name,
                        'journal_id': rec1.journal.id,
                        'date': rec1.date,
                        'invoice_date': rec1.date,
                        'line_ids': lines,
                        'expense_id': rec1.id, 
                    })
                    # sherahmed
    def GenerateSequence(self):
        for rec in self:
            # raise UserError([rec.state,rec.name])
            if not rec.seq_generate:

                current_date = self.date
                current_year = current_date.year
                current_month = current_date.month
                sequence_code = rec.journal.sequence_id.code
                sequence = rec.journal.sequence_id.next_by_code(sequence_code, sequence_date=current_date)
    #    raise UserError([sequence])

                rec['temp_name'] = f"{rec.journal.sequence_code_short}-{current_year}-{current_month}-{sequence}"
                rec['name'] = rec['temp_name']
                rec['seq_generate'] = True
            else:
                if not rec.temp_name:
                    rec['temp_name'] = ""
       
      
    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        # For Readonly
        self['readonly_check'] = True
        # sherahmed
        self.GenerateSequence()
       
       
        account_move = self.env['account.move'].search([('expense_id', '=', self.id)])
        # account_move['name'] = rec['temp_name']
        if len(account_move) == 0:

            self.create_expense_journal_entry()
       
       
       
    #    for rec in self:
    #         account_move = self.env['account.move'].search([('expense_id', '=', rec.id)])
    #         account_move['name'] = rec['temp_name']
       
    #    name = self.GenerateSequence(self.journal)
    #    self.name = name
    #    account_move= self.env['account.move'].search([('expense_id','=',self.id)])
    #    account_move['name']= name
    
       
    

    
    # def action_checked(self):
       

    #     self['approval_state']='check'
    #     self['checked_by'] = self.write_uid.id
    #     self['checked_timestamp'] = fields.Datetime.now()
        
    def action_verify(self):
        self['approval_state']='verify'
        self['verify_by'] = self.write_uid.id
        self['verify_timestamp'] = fields.Datetime.now()
        
    # def action_audit(self):
    #     self['approval_state']='audit'
    #     self['audit_by'] = self.write_uid.id
    #     self['audit_timestamp'] = fields.Datetime.now()
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
    
    # Approvals Expense
    approval_state_expense = fields.Selection(selection=EXPENSE_STATES, string="Approval Status",copy=False,)

    prepare_expense = fields.Many2one("res.users", string="Prepared expense",copy=False)
    prepare_expense_timestamp = fields.Datetime(strng="Prepared expense Timestamp" ,copy=False, readonly=True)
    verified_expense = fields.Many2one("res.users", string="Verified expense",copy=False)
    verified_expense_timestamp = fields.Datetime(strng="Verified expense Timestamp" ,copy=False, readonly=True)
    approve_expense = fields.Many2one("res.users", string="Approve By COO expense",copy=False)
    approve_expense_timestamp = fields.Datetime(strng="Approve By COO expense Timestamp" ,copy=False , readonly=True)
    
    def action_prepared_expense(self):
        self['approval_state_expense']='prepared'
        self['prepare_expense'] = self.write_uid.id
        self['prepare_expense_timestamp'] = fields.Datetime.now()
        # self['readonly_check'] = True
        
        # sherahmed
        
        self.GenerateSequence()
        account_move = self.env['account.move'].search([('expense_id', '=', self.id)])
        # account_move['name'] = rec['temp_name']
        if len(account_move) == 0:

            self.create_expense_journal_entry()
            
        # self.create_expense_journal_entry()
        # raise UserError(account_move_obj.name)
        
        # for rec in self:
        #     account_move = self.env['account.move'].search([('expense_id', '=', rec.id)])
        #     account_move['name'] = rec['temp_name']
        # self.name = name
        # account_move= self.env['account.move'].search([('expense_id','=',self.id)])
        # account_move['name']= name
        
    
    
    def action_verify_expense(self):
        self['approval_state_expense']='verify'
        self['verified_expense'] = self.write_uid.id
        self['verified_expense_timestamp'] = fields.Datetime.now()

        
    def action_approve_expense(self):
        self['approval_state_expense']='approve'
        self['approve_expense'] = self.write_uid.id
        self['approve_expense_timestamp'] = fields.Datetime.now()
    
    
    
    # Reject 
    
    
    reject_note = fields.Text(string="Rejection Note Quotation", readonly=True)
    
    
    
    
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'expense.module',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        
    
    
    
    
    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        landed_costs_lines = self.expense_line.filtered(lambda line: line.is_landed_costs_line)

        landed_costs = self.env['stock.landed.cost'].create({
            'expense_bill_id': self.id,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.property_account_expense_id.id,
                'price_unit': self.env.company.currency_id._convert(l.value, self.env.company.currency_id, self.env.company, l.expense_module_id.date),
                'split_method': l.product_id.split_method_landed_cost or 'equal',
                'analytic_distribution_landed_cost':l.analytical_field
            }) for l in landed_costs_lines],
        })
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])

    def action_view_landed_costs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        domain = [('id', 'in', self.landed_costs_ids.ids)]
        context = dict(self.env.context, default_expense_bill_id=self.id)
        views = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_tree2').id, 'tree'), (False, 'form'), (False, 'kanban')]
        return dict(action, domain=domain, context=context, views=views)
    
    @api.depends('expense_line', 'expense_line.is_landed_costs_line')
    def _compute_landed_costs_visible(self):
        for move in self:
            if move.landed_costs_ids:
                move.landed_costs_visible = False
            else:
                move.landed_costs_visible = any(line.is_landed_costs_line for line in move.expense_line)

    
    @api.depends('expense_line','expense_line.value','expense_line.general_item_type')    
    def compute_total_amount(self):
        for rec in self:
            rec['total_expense'] = 0
            if rec.expense_line:
                # if rec.expense_line.general_item_type == 'credit':
                #     rec['total_expense'] = sum(item['value'] for item in rec.expense_line)
                for expense in rec.expense_line:
                    if expense.general_item_type == 'credit':
                        rec.total_expense += expense.value
    @api.onchange("journal")
    def get_account_by_journal(self):
        if self.journal.id:
            if self.journal.is_miscellaneous_journal:
                self['account_id'] = self.journal.default_account_id.id
                # raise UserError("sa")
    def open_patient_appointment(self):
        return {
            'name': 'Journal Entry',
            'domain': [('expense_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
    @api.onchange("expense_line")
    def compute_line_item(self):
        sub_total = 0
        for line in self.expense_line:
            sub_total += line.value
            
        self.total_expense = sub_total
        
    
    def get_expense_count(self):
        count = self.env['account.move'].search_count([('expense_id', '=', self.id)])
        self.expense_count = count
    
    @api.model
    def create(self,vals):           
        vals['state']= 'draft'
        # sherahmed
        # vals['name'] = self.env['ir.sequence'].next_by_code('Exp_Seq')   
        vals['name'] = 'Draft'        
        # raise UserError("2")            
            # vals['create_date'] = self.posting_date
            # vals['posting_date'] = self.posting_date
            # vals['date'] = self.date
        res = super(RecordExpense,self).create(vals)
        return res
    
    # # @api.model
    # @api.model
    # def write(self,vals,a):
    #     # vals['total_expense']=self.total_expense
    #     exp=self.env['expense.module'].update({
    #             'total_expense': self.total_expense,
    #             })
    #     # res = super(RecordExpense,self).update(vals)
    #     # return res

    # NOMAN
    @api.depends("expense_line.value",'expense_line')
    def compute_credit_debit(self):
        self['total_debit'] = self['total_debit'] if self['total_debit'] else 0.0
        self['total_credit'] = self['total_credit']  if self['total_credit'] else 0.0
        total_debit = 0
        total_credit = 0
        for line in self.expense_line:
            if line.general_item_type == 'debit':
                total_debit += round(line.value,2)
            elif line.general_item_type == 'credit':
                total_credit += round(line.value,2)
        self['total_debit'] = round(total_debit,2)
        self['total_credit'] = round(total_credit,2)


    def check_debit_credit(self):
        
        if self.total_debit != self.total_credit:
            raise UserError('Debit and Credit should be equal')
        else:
            pass


            # sherahmed
    def server_post_expense_action(self):
        for rec in self:
            self.check_debit_credit()
            if (self.is_bank_payment == 'yes' and self.approval_state_expense == "approve") or (self.is_bank_payment == 'no' and self.approval_state_expense == "approve"):
                move = self.env['account.move'].search([('expense_id','=',rec.id)])
                
                rec.sudo().landed_costs_ids.reconcile_landed_cost()
                rec.write({
                    'state': 'posted',
                    'is_posted': '1',
                })
                if rec['state'] == 'posted':
                    move.action_post()
                
                # rec.write({
                #     'name': move.name,
                # })
                
                move.write({
                    'ref': move.name,
                })
                # raise UserError(rec['name'])
            else:
                raise UserError("Approval Required")
class AccountMove(models.Model):
    _inherit = 'account.move'
    expense_id = fields.Many2one('expense.module',string='Expense')
    cheque_number = fields.Char(string='Cheque Number')
    
    @api.model
    def getChequeNo(self):
        for rec in self:
            if rec.expense_id:
                rec['cheque_number'] = rec.expense_id.cheque_number
            elif rec.payment_id:
                rec['cheque_number'] = rec.payment_id.check_number
            
    

    def button_draft(self):
        for rec in self:
            if rec.expense_id:
                raise UserError("Record Expense JV is Not Reveseable")
        res = super(AccountMove, self).button_draft()
        return res
    
    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.expense_id:
                if rec.expense_id.state != "posted":
                    raise UserError("You Cannot Post Record Expense JV")           
        return res
class AccountJournal(models.Model):
    _inherit = 'account.journal'
    is_miscellaneous_journal = fields.Boolean(string = 'Is Miscellaneous Journal')


class ExpenseLine(models.Model):
    _name = 'expense.line'
    _description = "Expense Line"

    general_item_type = fields.Selection([('debit', 'Debit'), ('credit', 'Credit')], string='General Item Type')
    expense_module_id = fields.Many2one('expense.module')
    account = fields.Many2one('account.account',string='Account')
    account_group_id = fields.Many2one(related="account.group_id",string='Account Group')
    description = fields.Char(string='Short Description')

    trans_id = fields.Char(string='Transaction ID')
    partner = fields.Many2one('res.partner',string='Partner')
    paid_to = fields.Char(string='Paid To')
    # tags = fields.Many2one('account.analytic.account',string='Tags')
    analytic_precision = fields.Integer(string='Analytic Precision')

    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='move_line_id',
        string='Analytic lines',
    )
    analytical_field=fields.Json()

    currency_id = fields.Many2one('res.currency',string='Currency', related='account.company_id.currency_id',
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)
    value = fields.Float(string='Value',digits=(10, 2) )
    
    product_id = fields.Many2one('product.product',string="Product")
    is_landed_costs_line = fields.Boolean()

    company_id = fields.Many2one('res.company', string="Company",
        related='product_id.company_id')
    
    @api.onchange('product_id')
    def _onchange_product_id_landed_costs(self):
        if self.product_id.landed_cost_ok:
            self.is_landed_costs_line = True
            self.account = self.product_id.property_account_expense_id.id
        else:
            self.is_landed_costs_line = False
    
    @api.onchange('is_landed_costs_line')
    def _onchange_is_landed_costs_line(self):
        if self.is_landed_costs_line and self.product_id and self.product_id.detailed_type != 'service':
            self.is_landed_costs_line = False


    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id

class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    analytic_distribution_landed_cost = fields.Json(string="Analytic Account")