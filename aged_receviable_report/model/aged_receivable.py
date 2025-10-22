from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError



class AgedReceivableWizard(models.TransientModel):
    _name = 'aged.receivable.wizard'

    partner_ids = fields.Many2many(
        string='Partners',
        comodel_name='res.partner',
        domain=["&", ("customer_rank", ">", 0), ("is_company", "=", True)]
        
    )
    filter_type = fields.Selection(
        string='Invoice Filter',
        selection=[('all_customer', 'All Customer'), ('range_customer', 'Customer By Range')],
        default='all_customer'
        
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

        return self.env.ref('aged_receviable_report.action_aged_receivable').report_action(
            self,
            data=data,
        )
    
    def get_report_data(self):
        today = fields.Date.today()
        grouped_data = {}

        if not self.partner_ids and not self.from_new_code and not self.to_new_code:
            partners = self.env['res.partner'].search([]).filtered(lambda x: x.customer_rank > 0 and x.is_company)
        elif self.from_new_code and self.to_new_code:
            partners = self.get_sequential_data()
        else:
            partners = self.partner_ids


        for partner in partners:
            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('credit', '<=', 0),
                ('matching_number', '=', False),
                ('account_id', '=', partner.property_account_receivable_id.id)
            ])

            invoices = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice', 'entry']),
                ('invoice_date', '<=', self.date_filter),
                ('state', '=', 'posted'),
                '|',
                ('id', 'in', move_lines.mapped('move_id').ids),
                ('partner_id', '=', partner.id),
            ]).filtered(lambda x: x.payment_state in ['not_paid', 'partial'])

            partner_data = {'bills': []}
            sum_15, sum_31, sum_46, sum_61, sum_75, sum_75_plus = [], [], [], [], [], []

            for invoice in invoices:
                exact_days = (today - invoice.invoice_date).days if invoice.invoice_date else 0
                over_due = (today - invoice.invoice_date_due).days if invoice.invoice_date_due else 0

                if (
                    invoice.invoice_payment_term_id and
                    invoice.invoice_payment_term_id.line_ids and
                    len(invoice.invoice_payment_term_id.line_ids) > 0
                ):
                    credit_days = invoice.invoice_payment_term_id.line_ids[0].days
                else:
                    credit_days = (invoice.invoice_date_due - invoice.invoice_date).days if invoice.invoice_date and invoice.invoice_date_due else 0

                aging_bucket = self._get_aging_bucket(exact_days)
                currency_id = invoice.currency_id.name
                currency_rate = invoice.currency_rate

                if aging_bucket == '1-15 Days':
                    sum_15.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                elif aging_bucket == '16-30 Days':
                    sum_31.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                elif aging_bucket == '31-45 Days':
                    sum_46.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                elif aging_bucket == '46-60 Days':
                    sum_61.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                elif aging_bucket == '61-75 Days':
                    sum_75.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                elif aging_bucket == '75+ Days':
                    sum_75_plus.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(
                        line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))

                if int(invoice.amount_residual) != 0:
                    bill_data = {
                        'narration': partner.x_studio_new_code,
                        'partner_name': partner.name,
                        'name': invoice.name,
                        'date': invoice.invoice_date,
                        'over_due_days': exact_days - credit_days,
                        'over_due': over_due,
                        'exact': exact_days,
                        'credit': credit_days,
                        'due_date': invoice.invoice_date_due,
                        'amount_due': (
                            abs(invoice.amount_residual) if invoice.amount_residual > 0 else
                            abs(sum(line.debit if line.credit == 0 else line.credit for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id and line.partner_id == partner)) if invoice.line_ids else 0
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

        return {
            'doc_ids': self.ids,
            'doc_model': 'aged.receivable.wizard',
            'grouped_data': grouped_data,
            'recorded_date': self.date_filter.strftime('%d-%b-%Y'),
            'report_date': today.strftime('%d-%b-%Y') if today else '',
            'partners_ids': partners.ids
        }


    def select_data_for_selection(self):
        partners=self.env['res.partner'].search([('customer_rank','>',0),('is_company','=',True)])
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
        if self.filter_type == 'range_customer':
            if self.from_customer_new_code_id:
                self.from_new_code = self.from_customer_new_code_id
            else:
                self.from_new_code = ''
        else:
            self.from_customer_new_code_id=None
            self.from_new_code = None


    @api.onchange('to_customer_new_code_id','filter_type')
    def _onchange_to_partner_id(self):
        if self.filter_type == 'range_customer':
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
        # genarate_number = lambda code: "0"+str(code[0]) if len(str(code[0]))<2 else "00"+str(code[0]) + "-" +"0"+str(code[1]) if len(str(code[1]))<2 else "00"+str(code[1])
        new_codes=[genarate_number(code) for code in codes]
        # raise UserError(str(new_codes))                    
                                

        res=self.env['res.partner'].search([('x_studio_new_code','in',new_codes)],order="x_studio_new_code asc")
        # end_num=self.env['res.partner'].search([('new_code','in',self.to_new_code)]).id
        # res = []
        # while start_num <= end_num:
        #     partner = self.env['res.partner'].browse(start_num)
        #     if partner:
        #         res.append(partner)
        #     start_num += 1
        return res         

    def get_grand_total(self,basket,partners=None,date=None):

        if not partners:
            partners=self.env['res.partner'].search([],order="x_studio_new_code asc")
        else:
            partners=self.env['res.partner'].browse(partners)
        # raise UserError(str(date))

        # invoices=self.env['account.move'].search([('payment_state','not in',['paid','partial']),('move_type','=','out_invoice'),('partner_id','in',partners.ids),('state','=','posted'),('invoice_date','<=',date)])
        # raise UserError(str(invoices))
        for partner in partners:
            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('credit', '<=', 0),#
                # '|',  # Start of OR condition
                # ('matching_number', 'in', ['p', 'P']),
                ('matching_number', '=', False),
                ('account_id', '=', partner.property_account_receivable_id.id)
            ])

            invoices = self.env['account.move'].search([
                    ('move_type', 'in', ['out_invoice', 'entry']),
                    ('invoice_date', '<=', date),
                    ('state', '=', 'posted'),  # Ensure the invoice is posted
                    '|',  # Start of OR condition
                    ('id', 'in', move_lines.mapped('move_id').ids),
                    ('partner_id', 'in', partners.ids),  # Changed '=' to 'in'
                ]).filtered(lambda x: x.payment_state in ['not_paid', 'partial'])


            filtered_invoices=[]
            if basket.get('start')==-1:
                filtered_invoices=invoices.filtered(lambda inv: (fields.Date.today() - inv.invoice_date_due).days <=0)

            elif basket.get('start') and basket.get('end'):
                filtered_invoices=invoices.filtered(lambda inv: basket.get('end')>= (fields.Date.today() - inv.invoice_date_due).days >= basket.get('start'))
            elif basket.get('end'):
                filtered_invoices=invoices.filtered(lambda inv: basket.get('end')<(fields.Date.today() - inv.invoice_date_due).days )
            else: 
                filtered_invoices=invoices
                

            # amounts=filtered_invoices.mapped(lambda x:  int(x.amount_residual * x.currency_rate) if x.currency_id.name != 'PKR' else int(x.amount_residual))
            # total_amount=sum(amounts)
            # amounts = filtered_invoices.mapped(lambda x: 
            #     int(x.amount_residual * x.currency_rate) if x.currency_id.name != 'PKR' else int(x.amount_residual) if x.amount_residual > 0 else 
            #     sum(abs(line.amount_residual) for line in x.line_ids if line.account_id == partners.property_account_receivable_id)
            # )
            amounts = filtered_invoices.mapped(lambda x: 
                int(x.amount_residual * x.currency_rate) if x.currency_id.name != 'PKR' else 
                (int(x.amount_residual) if x.amount_residual > 0 else 
                sum(abs(line.debit if line.credit == 0 else line.credit) for line in x.line_ids if (line.account_id == partner.property_account_receivable_id and line.partner_id == partner)))
            )
        # raise UserError(amounts)
        total_amount=sum(amounts)

        return total_amount if total_amount else 0   



    def sort_invoices_by_date(self, invoices):
        """
        Sorts a list of invoice dictionaries by invoice date, oldest first.
        :param invoices: List of dictionaries containing invoice data.
        :return: Sorted list of invoice dictionaries.
        """
        return sorted(invoices, key=lambda x: x.get('date', ''), reverse=False)
                        
                
    def get_report(self):
        today = fields.Date.today()
        grouped_data = {}
        # If partner_ids is empty, get all partners
        if not self.partner_ids and not self.from_customer_new_code_id and not self.to_customer_new_code_id:
            # raise UserError('1')
            partners = self.env['res.partner'].search([], order='x_studio_new_code asc').filtered(lambda x:x.customer_rank > 0)
        elif self.from_new_code and self.to_new_code:
            partners = self.get_sequential_data()   
            # raise UserError(str(partners))
            # raise UserError(f"{self.from_new_code_id.id} {self.to_new_code_id.id}")
        else:
            # raise UserError('2')
            partners = self.partner_ids

        for partner in partners:
            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('credit', '<=', 0),
                # '|',  # Start of OR condition
                # ('matching_number', 'in', ['p', 'P']),
                ('matching_number', '=', False),
                ('account_id', '=', partner.property_account_receivable_id.id)
            ])

            # raise UserError(str(move_lines.read()))

            # invoices = self.env['account.move'].search([('partner_id', '=', partner.id), ('move_type', '=', 'out_invoice'),('invoice_date','<=', self.date_filter)], order="invoice_date asc").filtered(lambda x:x.state == 'posted' and  x.payment_state not in  ['paid','partial'])
            invoices = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice', 'entry']),
                ('invoice_date', '<=', self.date_filter),
                ('state', '=', 'posted'),  # Ensure the invoice is posted
                '|',  # Start of OR condition
                ('id', 'in', move_lines.mapped('move_id').ids),
                ('partner_id', '=', partner.id),  # Changed '=' to 'in'
            ]).filtered(lambda x: x.payment_state in ['not_paid', 'partial'])
            
            partner_data = {
                'invoices': []
            }
            
            sum_15=[]
            sum_31=[]
            sum_46=[]
            sum_61=[]
            sum_75=[]
            sum_75_plus=[]            
            for invoice in invoices:
                # if self.date_filter != invoice.invoice_date:
                exact_days = (today - invoice.invoice_date).days if invoice.invoice_date else 0
                over_due = (today - invoice.invoice_date_due).days if invoice.invoice_date_due else 0
                if (
                    invoice.invoice_payment_term_id
                    and invoice.invoice_payment_term_id.line_ids
                    and len(invoice.invoice_payment_term_id.line_ids) > 0
                ):
                    credit_days = invoice.invoice_payment_term_id.line_ids[0].days
                else:
                    # credit_days = None  # Or a default value

                    # credit_days = None  # Or any default value you prefer
                    credit_days = (invoice.invoice_date_due - invoice.invoice_date).days if invoice.invoice_date and invoice.invoice_date_due else 0

                # credit_days = (invoice.invoice_date_due - invoice.invoice_date).days if invoice.invoice_date and invoice.invoice_date_due else 0
                aging_bucket = self._get_aging_bucket(exact_days)
                currency_id= invoice.currency_id.name
                currency_rate= invoice.currency_rate

                # raise UserError(currency_id)
                # Filter out empty or zero-value data
                # if not all([invoice.invoice_date, invoice.invoice_date_due, invoice.amount_residual, aging_bucket]):
                #     continue


                if aging_bucket == '1-15 Days':
                    sum_15.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                if aging_bucket == '16-30 Days':
                    sum_31.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                if aging_bucket == '31-45 Days':
                    sum_46.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                if aging_bucket == '46-60 Days':
                    sum_61.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                if aging_bucket == '61-75 Days':
                    sum_75.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))
                if aging_bucket == '75+ Days':
                    sum_75_plus.append(invoice.amount_residual if invoice.amount_residual > 0 else sum(line.amount_residual for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id))

                if int(invoice.amount_residual) != 0:
                    invoice_data = {
                        'narration': self.env['res.partner'].browse(partner.id).x_studio_new_code,
                        'partner_name': partner.name,
                        'name': invoice.name,
                        'date': invoice.invoice_date,
                        'over_due_days': exact_days - credit_days,
                        'over_due' : over_due,
                        'exact': exact_days,
                        'credit': credit_days,
                        'due_date': invoice.invoice_date_due,
                        'amount_due': (
                            abs(invoice.amount_residual) if invoice.amount_residual > 0 else 
                            abs(sum(line.debit if line.credit == 0 else line.credit for line in invoice.line_ids if line.account_id == partner.property_account_receivable_id and line.partner_id == partner)) if invoice.line_ids else 0
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

                    # invoice_data = self.sort_invoices_by_date(invoice_data)
                    
                    partner_data['invoices'].append(invoice_data)

                    partner_data['invoices'] = self.sort_invoices_by_date(partner_data['invoices'])
                
                if partner_data['invoices']:
                    grouped_data[partner.id] = partner_data
            
        data = {
            'doc_ids': self.ids,
            'doc_model': 'aged.receivable.wizard',
            'grouped_data': grouped_data,
            'recorded_date': self.date_filter.strftime('%d-%b-%Y'),
            'report_date': today.strftime('%d-%b-%Y') if today else '',
            'partners_ids':partners.ids
        }   
        # raise UserError(str(data))
        data=self.sort_bills(data)
        return self.env.ref('aged_receviable_report.action_report_aged_receivable').report_action(self, data=data)
    
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
            bills = sorted_data['grouped_data'][partner_id]['invoices']
            
            # Sort bills first by narration, then by over_due_days in descending order
            sorted_bills = sorted(bills, key=lambda x: (x['narration'], -x['over_due_days']))
            
            # Update the bills in the data structure
            sorted_data['grouped_data'][partner_id]['invoices'] = sorted_bills
        
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
