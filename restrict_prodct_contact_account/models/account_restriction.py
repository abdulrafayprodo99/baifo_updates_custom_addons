from odoo import fields, models, api

class AccountAccount(models.Model):
    _inherit="account.account"


    is_published = fields.Boolean(string='Published', default=True, readonly=True)



    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['is_published'] = False
            val['deprecated'] = True
        return super().create(vals)



    def action_prepared(self):
        # Prepare the values to update
        values = {
            'approval_state': 'prepared',
            'prepared_by': self.write_uid.id,
            'prepared_timestamp': fields.Datetime.now(),
            'deprecated': True # Make the record inactive
        }
        # Write the changes to the records
        self.write(values)

    def action_approve(self):
        # Prepare the values to update
        values = {
            'approval_state': 'approve',
            'Approve_by': self.write_uid.id,
            'approve_timestamp': fields.Datetime.now(),
            'readonly_check': True,
            'deprecated': False, # Make the record active again
            'is_published' : True
        }
        
        # Write the changes to the records
        self.write(values)
