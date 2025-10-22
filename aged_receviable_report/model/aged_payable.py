from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError




class AgedReceivableWizard(models.TransientModel):
    _name = 'aged.payable.wizard'


    employee_partner_ids = fields.Many2many(
        'res.partner',
        string="Employee Partners",
        compute="_compute_employee_partner_ids",
        store=False
    )


    employee_partner_ids = fields.Many2many(
        'res.partner',
        string="Employee Partners",
        compute="_compute_employee_partner_ids",
        store=False
    )

    bill_partner_ids = fields.Many2many(
        'res.partner',
        string='Bill Partners'
    )

    @api.depends('date_filter')
    def _compute_employee_partner_ids(self):
        """Fetch all partner IDs linked to employees"""
        employee_partners = self.env['hr.employee'].sudo().search([]).mapped('address_home_id.id')
        for record in self:
            record.employee_partner_ids = employee_partners


    @api.onchange('employee_partner_ids')
    def _onchange_employee_partner_ids(self):
        """Dynamically filter bill_partner_ids to exclude employee partners"""
        if self.employee_partner_ids:
            return {
                'domain': {
                    'bill_partner_ids': [
                        '&',
                        ('supplier_rank', '>', 0),
                        ('type', '!=', 'delivery'),
                        ('id', 'not in', self.employee_partner_ids.ids)
                    ]
                }
            }
    filter_type = fields.Selection(
        string='Invoice Filter',
        selection=[('all_supplier', 'All Vendor'), ('range_supplier', 'Vendor By Range')],
        default='all_supplier'
        
    )

    from_customer_new_code_id = fields.Selection(
        string='From Partner ',
        selection='select_data_for_selection'
    )
    to_customer_new_code_id = fields.Selection(
        string='To Partner ',
        selection='select_data_for_selection'
    )

        
        
    def export_xlsx(self):
        data = self.get_report_data()
        # raise UserError(str(data))

        return self.env.ref('aged_receviable_report.report_action_xlsx').report_action(
            self,
            data=data,
        )
    
    def get_report_data(self):
        today = fields.Date.today()
        grouped_data = {}

        if not self.bill_partner_ids and not self.from_new_code and not self.to_new_code:
            partners = self.env['res.partner'].search([]).filtered(lambda x: x.supplier_rank > 0 and x.is_company)
        elif self.from_new_code and self.to_new_code:
            partners = self.get_sequential_data()
        else:
            partners = self.bill_partner_ids

        for partner in partners:
            move_lines = self._get_move_lines(partner)
            credit = sum(map(lambda line: line.credit, move_lines))
            debit = 0
            matching_numbers = [x.matching_number for x in move_lines if x.matching_number]
            move_ids = list(set(map(lambda line: line.move_id.id, move_lines)))

            lines = self.env['account.move.line'].search([
                ('matching_number', 'in', matching_numbers),
                ('debit', '>', 0),
                ('account_id', '=', partner.property_account_payable_id.id),
                ('partner_id', '=', partner.id)
            ])
            if lines:
                debit = sum(map(lambda x: x.debit, lines))

            partner_data = {'bills': []}
            sum_15, sum_31, sum_46, sum_61, sum_75, sum_75_plus = [], [], [], [], [], []

            for bill in move_lines:
                exact_days = (today - bill.date).days if bill.date else 0
                if (
                    bill.move_id
                    and bill.move_id.invoice_payment_term_id
                    and bill.move_id.invoice_payment_term_id.line_ids
                ):
                    credit_days = bill.move_id.invoice_payment_term_id.line_ids[0].days
                else:
                    credit_days = (bill.date_maturity - bill.date).days if bill.date and bill.date_maturity else 0

                if bill.move_name.lower().startswith('jv'):
                    over_due = (today - bill.date).days if bill.date else 0
                else:
                    over_due = (today - bill.date_maturity).days if bill.date_maturity else 0

                aging_bucket = self._get_aging_bucket(exact_days)
                currency_id = bill.currency_id.name
                currency_rate = bill.move_id.currency_rate

                if aging_bucket == '1-15 Days':
                    sum_15.append(abs(bill.amount_residual))
                elif aging_bucket == '16-30 Days':
                    sum_31.append(abs(bill.amount_residual))
                elif aging_bucket == '31-45 Days':
                    sum_46.append(abs(bill.amount_residual))
                elif aging_bucket == '46-60 Days':
                    sum_61.append(abs(bill.amount_residual))
                elif aging_bucket == '61-75 Days':
                    sum_75.append(abs(bill.amount_residual))
                elif aging_bucket == '75+ Days':
                    sum_75_plus.append(abs(bill.amount_residual))

                if int(bill.amount_residual) != 0:
                    bill_data = {
                        'narration': partner.x_studio_new_code,
                        'partner_name': partner.name,
                        'name': bill.move_name,
                        'date': bill.date,
                        'over_due_days': exact_days - credit_days,
                        'over_due': over_due,
                        'exact': exact_days,
                        'credit': credit_days,
                        'due_date': bill.date_maturity,
                        'amount_due': abs(bill.amount_residual),
                        'aging_bucket': aging_bucket,
                        'total_15': sum_15,
                        'total_31': sum_31,
                        'total_46': sum_46,
                        'total_61': sum_61,
                        'total_75': sum_75,
                        'total_75_plus': sum_75_plus,
                        'currency_name': currency_id,
                        'currency_rate': currency_rate
                    }
                    partner_data['bills'].append(bill_data)

            if partner_data['bills']:
                partner_data['bills'] = sorted(partner_data['bills'], key=lambda k: k['date'])
                grouped_data[partner.id] = partner_data

        return {
            'doc_ids': self.ids,
            'doc_model': 'aged.payable.wizard',
            'grouped_data': grouped_data,
            'recorded_date': self.date_filter.strftime('%d-%b-%Y'),
            'report_date': today.strftime('%d-%b-%Y') if today else '',
            'partners_ids': partners.ids
        }

    def select_data_for_selection(self):
        partners=self.env['res.partner'].search([('supplier_rank','>',0),('is_company','=',True)])
        partners_code=[(
            partner.x_studio_new_code,f"{partner.x_studio_new_code}-{partner.name}"
            )
            for partner in partners if partner.x_studio_new_code
        ]
        partners_code.sort(key=lambda x:x[0])
        # raise UserError(partners_code)
        return partners_code

    from_new_code = fields.Char(
        string='From New Code'
    )
    
    to_new_code = fields.Char(
        string='To New Code'
    )

    date_filter = fields.Date(
        string='Select Date',
        default=datetime.today()
        
    )

    @api.onchange('from_customer_new_code_id','filter_type')
    def _onchange_from_partner_id(self):
        # raise UserError("raise ")
        if self.filter_type == 'range_supplier':
            if self.from_customer_new_code_id:
                self.from_new_code = self.from_customer_new_code_id
            else:
                self.from_new_code = ''
        else:
            self.from_customer_new_code_id=None
            self.from_new_code = None


    @api.onchange('to_customer_new_code_id','filter_type')
    def _onchange_to_partner_id(self):
        if self.filter_type == 'range_supplier':
            if self.to_customer_new_code_id:
                self.to_new_code = self.to_customer_new_code_id
            else:
                self.to_new_code = ''
        else:
            self.to_customer_new_code_id=None
            self.to_new_code=None

    def get_sequential_data(self):
        # pass
        def genarate_number(code):
            first= "0"+str(code[0]) if len(str(code[0]))<2 else str(code[0])
            second= "00"+str(code[1]) if len(str(code[1]))<2 else "0"+str(code[1])
            return f"{first}-{second}"
        self.ensure_one()

        fromFirst,fromSecond=self.from_new_code.split('-')
        fromCode=(int(fromFirst),int(fromSecond))
        
        toFirst,toSecond=self.to_new_code.split('-')
        toCode=(int(toFirst),int(toSecond))

        parentCodes=[ parentCode  for parentCode in range(int(fromFirst),int(toFirst)+1)]
        codes=[]
        for parentCode in parentCodes:
            if parentCode == toCode[0]:
                for i in range(1,toCode[1]+1):
                    codes.append((parentCode,i))
            elif parentCode == fromCode[0]:
                for i in range(fromCode[1],101):
                    codes.append((parentCode,i))
            else:
                for i in range(1,101):
                    codes.append((parentCode,i))
        new_codes=[genarate_number(code) for code in codes]                  
                                

        res=self.env['res.partner'].search([('x_studio_new_code','in',new_codes)],order="x_studio_new_code asc")
        return res            
    
    def get_grand_total(self,basket,partners=None,date=None):

        if not partners:
            partners=self.env['res.partner'].search([],order="x_studio_new_code asc")
        else:
            partners=self.env['res.partner'].browse(partners)

        for partner in partners:
            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('debit', '<=', 0),
                # Check if matching_number is False or equal to 'p'
                # '|',  # Start of OR condition
                ('matching_number', '=', False),
                ('account_id', '=', partner.property_account_payable_id.id)
            ])
            invoices = self.env['account.move'].search([
                
                ('move_type', 'in', ['in_invoice', 'entry']),
                ('invoice_date', '<=', date),
                ('state', '=', 'posted'),  # Ensure the invoice is posted
                '|',  # Start of OR condition
                ('id', 'in', move_lines.mapped('move_id').ids),
                ('partner_id', '=', partner.id), 
            ]).filtered(lambda x: x.payment_state in ['not_paid', 'partial'])
            filtered_invoices=None
            if basket.get('start')==-1:
                filtered_invoices=invoices.filtered(lambda inv: (fields.Date.today() - inv.invoice_date_due).days <=0)

            elif basket.get('start') and basket.get('end'):
                filtered_invoices=invoices.filtered(lambda inv: basket.get('end')>= (fields.Date.today() - inv.invoice_date_due).days >= basket.get('start'))
            elif basket.get('end'):
                filtered_invoices=invoices.filtered(lambda inv: basket.get('end')<=(fields.Date.today() - inv.invoice_date_due).days )
            else: 
                filtered_invoices=invoices

            amounts = filtered_invoices.mapped(lambda x: 
                int(x.amount_residual * x.currency_rate) if x.currency_id.name != 'PKR' else 
                (int(x.amount_residual) if x.amount_residual > 0 else 
                sum(abs(line.balance) for line in x.line_ids if (line.account_id == partner.property_account_payable_id and line.partner_id == partner)))
            )
        total_amount=sum(amounts)
        # return filtered_invoices
        return total_amount if total_amount else 0  

    def _get_move_lines(self,partner):

        move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('parent_state','=','posted'),
                ('amount_residual', '!=', 0),
                ('account_id', '=', partner.property_account_payable_id.id)
            ])

        credit_lines =  move_lines.filtered(lambda x: x.debit <= 0)
        # debit_lines =  move_lines - credit_lines
        # credit_lines =  credit_lines.filtered(lambda x: x.amount_residual != 0)
        # credit_lines_without_matching =  credit_lines.filtered(lambda x: x.matching_number == False)
        # credit_lines_with_matching =  credit_lines - credit_lines_without_matching
        # credit_lines_matching_with_debit = []
        # for line in credit_lines_with_matching:
        #     lines = debit_lines.filtered(lambda x: x.matching_number == line.matching_number) 
        #     if lines:
        #         credit_lines_matching_with_debit.append(line.id)
                
        # raise UserError(f"{len(move_lines)} == {len(credit_lines)} == {len(debit_lines)} == {len(credit_lines_matching_with_debit)} == {len(credit_lines_without_matching)}")
        # final_lines = list(map(lambda x :x.id,credit_lines_without_matching))

        # final_lines.extend(credit_lines_matching_with_debit)
        # final_lines = self.env['account.move.line'].browse(final_lines)
        # raise UserError(len(final_lines))
        return credit_lines
    def get_report(self):
        today = fields.Date.today()
        grouped_data = {}

        # If partner_ids is empty, get all partners
        if not self.bill_partner_ids and not self.from_new_code and not self.to_new_code:
            partners = self.env['res.partner'].search([]).filtered(lambda x:x.supplier_rank > 0 )

        elif self.from_new_code and self.to_new_code:
            partners = self.get_sequential_data()
        else:
            partners = self.bill_partner_ids

        for partner in partners:
            move_lines = self._get_move_lines(partner)
            credit  =  sum(map(lambda line:line.credit,move_lines))
            debit = 0
            # matching_numbers = list(map(lambda line:line.matching_number,move_lines))
            matching_numbers = [x.matching_number for x in move_lines if x.matching_number]
            move_ids = list(set(map(lambda line:line.move_id.id,move_lines)))
            lines = self.env['account.move.line'].search([
                ('matching_number', 'in', matching_numbers),
                ('debit', '>', 0),
                ('account_id', '=', partner.property_account_payable_id.id),
                ('partner_id', '=', partner.id)
            ])
            if lines:
                debit = sum(map(lambda x:x.debit,lines))
        
            bills = self.env['account.move'].search([
                # ('move_type', 'in', ['in_invoice', 'entry']),
                # ('invoice_date', '<=', self.date_filter),
                # ('state', '=', 'posted'),  # Ensure the invoice is posted
                # '|',  # Start of OR condition
                ('id', 'in', move_ids),
            ])
            partner_data = {
                'bills': []
            }
            sum_15=[]
            sum_31=[]
            sum_46=[]
            sum_61=[]
            sum_75=[]
            sum_75_plus=[]            
            for bill in move_lines:
                if bill.move_name.lower().startswith('jv'):
                    # exact_days = '-'
                    # credit_days = '-'
                    exact_days = (today - bill.date).days if bill.date else 0
                    if (
                        bill.move_id
                        and bill.move_id.invoice_payment_term_id
                        and bill.move_id.invoice_payment_term_id.line_ids
                        and len(bill.move_id.invoice_payment_term_id.line_ids) > 0
                    ):
                        credit_days = bill.move_id.invoice_payment_term_id.line_ids[0].days
                    else:
                        # credit_days = None  # Or any default value you prefer
                        credit_days = (bill.date_maturity - bill.date).days if bill.date and bill.date_maturity else 0

                    # credit_days = (bill.date_maturity - bill.date).days if bill.date and bill.date_maturity else 0
                    over_due = (today - bill.date).days if bill.date else 0
                else:
                    exact_days = (today - bill.date).days if bill.date else 0
                    # credit_days = (bill.date_maturity - bill.date).days if bill.date and bill.date_maturity else 0
                    if (
                        bill.move_id
                        and bill.move_id.invoice_payment_term_id
                        and bill.move_id.invoice_payment_term_id.line_ids
                        and len(bill.move_id.invoice_payment_term_id.line_ids) > 0
                    ):
                        credit_days = bill.move_id.invoice_payment_term_id.line_ids[0].days
                    else:
                        # credit_days = None
                        credit_days = (bill.date_maturity - bill.date).days if bill.date and bill.date_maturity else 0
                    over_due = (today - bill.date_maturity).days if bill.date_maturity else 0

                aging_bucket = self._get_aging_bucket(exact_days if isinstance(exact_days, int) else 0)
                currency_id = bill.currency_id.name
                currency_rate = bill.move_id.currency_rate
                
                # credit =  bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id)
                
                if aging_bucket == '1-15 Days':
                    sum_15.append(abs(bill.amount_residual))
                    # sum_15.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if aging_bucket == '16-30 Days':
                    sum_31.append(abs(bill.amount_residual))
                    # sum_31.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if aging_bucket == '31-45 Days':
                    sum_46.append(abs(bill.amount_residual))
                    # sum_46.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if aging_bucket == '46-60 Days':
                    sum_61.append(abs(bill.amount_residual))
                    # sum_61.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if aging_bucket == '61-75 Days':
                    sum_75.append(abs(bill.amount_residual))
                    # sum_75.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if aging_bucket == '75+ Days':
                    sum_75_plus.append(abs(bill.amount_residual))
                    # sum_75_plus.append(bill.amount_residual if bill.amount_residual > 0 else sum(line.debit for line in bill.line_ids if line.account_id == partner.property_account_payable_id))
                if int(bill.amount_residual) != 0:
                    bill_data = {
                        'narration': self.env['res.partner'].browse(partner.id).x_studio_new_code,
                        'partner_name': partner.name,
                        'name': bill.move_name,
                        'date': bill.date,
                        'over_due_days':exact_days - credit_days ,
                        'over_due': over_due ,
                        'exact': exact_days,
                        'credit': credit_days,
                        'due_date': bill.date_maturity,
                        'amount_due': (
                            abs(bill.amount_residual)
                            # abs(credit-debit)
                            # abs(bill.amount_residual) if bill.amount_residual > 0 else 
                            # abs(sum(line.debit if line.credit == 0 else line.credit for line in bill.line_ids if line.account_id == partner.property_account_payable_id and line.partner_id == partner)) if bill.line_ids else 0
                        ),
                        'aging_bucket': aging_bucket,
                        'total_15': sum_15,
                        'total_31': sum_31,
                        'total_46': sum_46,
                        'total_61': sum_61,
                        'total_75': sum_75,
                        'total_75_plus': sum_75_plus,
                        'currency_name': currency_id,
                        'currency_rate': currency_rate
                    }
                    partner_data['bills'].append(bill_data)

                if partner_data['bills']:
                    partner_data['bills'] = sorted(partner_data['bills'], key=lambda k: k['date'])
                    grouped_data[partner.id] = partner_data
            data = {
                'doc_ids': self.ids,
                'doc_model': 'aged.payable.wizard',
                'grouped_data': grouped_data,
                'recorded_date': self.date_filter.strftime('%d-%b-%Y'),
                'report_date': today.strftime('%d-%b-%Y') if today else '',
                'partners_ids':partners.ids
            }   

        data = self.sort_bills(data)
        
        return self.env.ref('aged_receviable_report.action_report_aged_payable').report_action(self, data=data)
    


    def sort_bills(self, data):
        """
        Sorts bills in grouped_data first by narration, then by over_due_days in descending order.
        
        Args:
            data (dict): Input data containing grouped_data with bills.
        
        Returns:
            dict: Data with sorted bills.
        """
        sorted_data = data.copy()
        
        # Iterate through each partner in grouped_data
        for partner_id in sorted_data['grouped_data']:
            # Get the bills for the current partner
            bills = sorted_data['grouped_data'][partner_id]['bills']
            
            # Sort bills first by narration, then by over_due_days in descending order
            # sorted_bills = sorted(bills, key=lambda x: (x['narration'], x['over_due_days']))
            sorted_bills = sorted(bills, key=lambda x: (x['narration'], -x['over_due_days']))

            
            # Update the bills in the data structure
            sorted_data['grouped_data'][partner_id]['bills'] = sorted_bills
        
        return sorted_data


    def _get_aging_bucket(self, due_days):
        if due_days <= 0:
            return 'Not Due'
        elif 1 <= due_days <= 15:
            return '1-15 Days'
        elif 16 <= due_days <= 30:
            return '16-30 Days'
        elif 31 <= due_days <= 45:
            return '31-45 Days'
        elif 46 <= due_days <= 60:
            return '46-60 Days'
        elif 61 <= due_days <= 75:
            return '61-75 Days'
        else:
            return '75+ Days'