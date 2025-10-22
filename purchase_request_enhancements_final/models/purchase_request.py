from odoo import models,fields,api,_
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit="purchase.request"

    cancel_note = fields.Text('Reason of Cancellation')

# Added draft_number field
    draft_number = fields.Char(string="Draft Number", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("approval_state", "initiated") == "initiated":
                if vals.get("name", False):
                    base_number = vals["name"][10:] if len(vals["name"]) > 10 else vals["name"]
                    vals["draft_number"] = f"Draft/{base_number.zfill(4)}"
                    vals["name"] = vals["draft_number"]  # Sync name with draft_number
                else:
                    vals["draft_number"] = self.env["ir.sequence"].next_by_code("purchase.request.draft")
                    vals["name"] = vals["draft_number"]  # Sync name with draft_number

            return super(PurchaseRequest, self).create(vals_list)
    def write(self, vals):
        for record in self:
            if vals.get("approval_state") and vals["approval_state"] != "initiated":
                if record.approval_state == "initiated":  # Only if transitioning from initiated
                    pr_sequence = self.env["ir.sequence"].next_by_code("purchase.request")
                    vals["name"] = pr_sequence  
                vals["draft_number"] = False  

        return super(PurchaseRequest, self).write(vals)

    # # Ensure action_prepared updates approval_state correctly (if not already defined)
    # def action_prepared(self):
    #     return self.write({"approval_state": "store_supervisors"})