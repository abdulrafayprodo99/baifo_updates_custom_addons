from odoo import api, fields, models,_
from odoo.exceptions import UserError


ATTESTATION_STATES = [
   ('prepared','Prepared'),
   ('approve','Approved'),
]
class Attestation(models.Model):
    _name = 'attestation.model'

    name = fields.Char('Attestation Name', required=True)
    attestation_type = fields.Selection([
        ('draft', 'RFQ'),
        ('purchase', 'PO')
    ], string='PO State')

    # Noman's Work

    doc_type = fields.Selection([
        ('so', 'SO'),
        ('po', 'PO'),
        ('sale_invoice', 'SI')
    ], string='Document Type')

    so_state = fields.Selection([
        ('sale', 'SO'),
        ('sq', 'SQ')
    ], string='SO State')
    
    attestation_content = fields.Html('Terms & Conditions')
    
    # Chart of Account


    
    approval_state = fields.Selection(selection=ATTESTATION_STATES, string="Approval Status",copy=False,)
    
   

    prepared_by = fields.Many2one("res.users", string="Prepared by",copy=False)
    prepared_timestamp = fields.Datetime(strng="Prepared Timestamp" , readonly=True,copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by",copy=False)
    approve_timestamp = fields.Datetime(strng="Approve Timestamp" , readonly=True,copy=False)
    # For Readonly
    readonly_check = fields.Boolean('Readonly Check',copy=False)
    
    reject_note = fields.Text(string="Rejection Note")

    def action_prepared(self):
        self['approval_state']='prepared'
        self['prepared_by'] = self.write_uid.id
        self['prepared_timestamp'] = fields.Datetime.now()
        
        
    def action_approve(self):
        self['approval_state']='approve'
        self['Approve_by'] = self.write_uid.id
        self['approve_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True

    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'attestation.model',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }





class VendorInherit(models.Model):
    _inherit = 'res.partner'

    attestation_rfq_id = fields.Many2one('attestation.model', string='RFQ T&C', domain=[('attestation_type','=','draft'),('approval_state', '=', 'approve')])
    attestation_po_id = fields.Many2one('attestation.model', string='PO T&C', domain=[('attestation_type','=','purchase'),('approval_state', '=', 'approve')])
    attestation_so_id = fields.Many2one('attestation.model', string='SO T&C', domain=[('so_state','=','sale'),('approval_state', '=', 'approve')])
    attestation_sq_id = fields.Many2one('attestation.model', string='SQ T&C', domain=[('so_state','=','sq'),('approval_state', '=', 'approve')])
    attestation_si_id = fields.Many2one('attestation.model', string='SI T&C', domain=[('doc_type','=','sale_invoice'),('approval_state', '=', 'approve')])



    


    