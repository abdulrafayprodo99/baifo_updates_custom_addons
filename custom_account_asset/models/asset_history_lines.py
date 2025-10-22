from odoo import models, fields, api

class AssetHistoryLines(models.Model):
    _name = "asset.history.lines"

    account_asset_id = fields.Many2one('account.asset', string="Account Asset")
    date = fields.Datetime(string="Date")
    transfer_from = fields.Many2one('asset.location', string="Transfer From")
    transfer_to = fields.Many2one('asset.location', string="Transfer To")
    transfer_detail = fields.Many2one('hr.employee', string="Transfer Detail")
    receiver_detail = fields.Many2one('hr.employee', string="Receiver Detail")
    remarks = fields.Char(string="Remarks")



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def name_get(self):
        result = []
        for employee in self:
            # Format: [ID] Employee Name
            name = f"{employee.employee_id} {employee.name}"
            result.append((employee.id, name))
        return result