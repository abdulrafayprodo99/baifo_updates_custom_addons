
from collections import defaultdict
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, plaintext2html


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))
        slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][slip.date or fields.Date().end_of(slip.date_to, 'month')] |= slip
        for journal_id in slip_mapped_data: 
            for slip_date in slip_mapped_data[journal_id]:
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': fields.Date().end_of(slip.date_to, 'month').strftime('%B %Y'),
                    'journal_id': journal_id,
                    # 'department_id': self.department_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
                    move_dict['narration'] += Markup('<br/>')
                    slip_lines = slip._prepare_slip_lines(date, line_ids)
                    line_ids.extend(slip_lines)

                for line_id in line_ids: 
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self._create_account_move(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True