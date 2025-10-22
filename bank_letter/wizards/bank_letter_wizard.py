from odoo import models, fields, api
import json
from num2words import num2words
import datetime

class BankLetterWizard(models.TransientModel):
    _name = 'bank.letter.wizard'
    _description = 'Wizard for Bank Letter Report'

    # bank_name = fields.Char(string="Bank Name", required=True)
    bank_id = fields.Many2one('res.bank', string="Bank", required=True)
    # account_number = fields.Char(string="Account Number", required=True)
    payslip_ids = fields.Many2many('hr.payslip', string="Payslips", required=True)

    def amount_to_words(self, amount):
        words = num2words(amount, lang="en")
        main_currency = "Rupee" if amount == 1 else "Rupees"
        sub_currency = "Paisa" if amount == 1 else "Paisas"
        rupees, paisas = int(amount), int(round((amount - int(amount)) * 100))
        words = f"{num2words(rupees, lang='en').title()} {main_currency}"
        words = words.replace(' And ', ' ').replace('-', ' ').replace(', ', ' ')
        if paisas:
            words += f" And {num2words(paisas, lang='en').title().replace('-', ' ').replace(', ', ' ')} {sub_currency}"
        return words
    
    def _get_address(self, bank_id):
        city = None
        if (bank_id.city and bank_id.state):
            city = f"{bank_id.city}, {bank_id.state.name}"
        elif (bank_id.city):
            city = bank_id.city
        elif (bank_id.state):
            city = bank_id.state.name

        address_lines = list(filter(None, [
            bank_id.street,
            bank_id.street2,
            city,
            bank_id.zip,
            bank_id.country.name
        ]))
        return address_lines
       
    def _prepare_data(self):
        payslips = []
        total_amount = 0
        for payslip in self.payslip_ids:
            amount = payslip.line_ids.filtered(lambda l: l.code == 'NET').total
            total_amount += amount
            payslips.append({
                'emp_code': payslip.id,
                'name': payslip.employee_id.name,
                'account': payslip.employee_id.bank_account_id.acc_number,
                'amount': '{:,}'.format(amount),
            })
        total_amount_iw = self.amount_to_words(total_amount)
        bank_name_parts = self.bank_id.name.split('-')
        if len(bank_name_parts) > 1:
            bank_name = bank_name_parts[0]
            account_number = bank_name_parts[1].replace('(', '').replace(')', '')
        else:
            bank_name = self.bank_id.name 
            account_number = ''
        # bank_name = self.bank_id.name.split('-')[0]
        # account_number = self.bank_id.name.split('-')[1].replace('(', '').replace(')', '')
        address = self._get_address(self.bank_id)
          
        data = {
            # "bank_name": self.bank_name,
            # "account_number": self.account_number,
            "bank_name": bank_name,
            "account_number": account_number,
            "address": address,
            "payslips": payslips,
            "total_amount": '{:,}'.format(total_amount),
            "total_amount_iw": total_amount_iw,
            "date": (datetime.datetime.now() + datetime.timedelta(hours=5)).strftime('%d-%b-%Y'),
        }
        return data
            
    def generate_pdf_report(self):
        data = self._prepare_data()
        return self.env.ref('bank_letter.bank_letter_pdf_report_action').report_action(self, data=data)

    def generate_excel_report(self):
        data = self._prepare_data()
        return self.env.ref('bank_letter.bank_letter_excel_report_action').report_action(self, data=data)
