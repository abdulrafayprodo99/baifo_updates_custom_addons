from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FunctionalLocation(models.Model):
    _name = 'functional.location'
    _description = 'Functional Location'
     
    # Saif Code Start Task_ID: 38937
    # _rec_name = ['location_id', 'location_name']

    sr_no = fields.Char(string="Sr No.", readonly=True)
    # location_id = fields.Char(string="Location ID", readonly=True)
    location_id = fields.Char(string="Location ID") #, readonly=True Saif Task_ID:38937
    location_name = fields.Char(string="Location ID")

    @api.model
    def create(self, vals):
        # Fetch the maximum sr_no in the table
        last_record = self.search([], order='sr_no desc', limit=1)
        last_sr_no = last_record.sr_no if last_record else 0
        new_sr = int(last_sr_no) + 1
        vals['sr_no'] = str(new_sr)

        # Generate a 4-digit location_id based on the new sr_no
        # vals['location_id'] = str(vals['sr_no']).zfill(4)

        # Call the super method to create the record
        return super(FunctionalLocation, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            display_name = ""
            if record.location_name:
                display_name = f"{record.location_name}"
            else:
                display_name = f"Functional Location - {record.id}"
            result.append((record.id, display_name))
        return result
