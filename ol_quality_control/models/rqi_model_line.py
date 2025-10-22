from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError
from datetime import datetime

class RqiModelLine(models.Model):
    _inherit="rqi.model.line"

    norm=fields.Float('Norm',related='point_id.norm')
    norm_unit=fields.Char('Norm Unit',related='point_id.norm_unit')
    status_qir = fields.Selection([
        ('approve', 'Approve'),
        ('not_approve', 'Not Approve'),
        ('compromised', 'Refer to PM'),
    ], string='Status', default='approve')

    # @api.onchange('status_qir')
    # def check_ready_state(self):
    #     for rec in self:
    #         if rec.status_qir=='compromised':
    #             # raise UserError(f"{rec.rqi_id.read()}")
    #             rec.rqi_id._origin.state_approval='ready'
                
            

class RqiModel(models.Model):
    _inherit="rqi.model"

    hide_approval=fields.Boolean("Approval Show",compute="_compute_show_approval")
    recent_ids=fields.Json("Recent Ids")
    gate_in_id=fields.Many2one(comodel_name='gate.in',string="Gate In",compute="_compute_gate_pass")
    purchase_order=fields.Many2one('purchase.order',"Purchase Order",compute="_compute_purchase_order")

    def _compute_purchase_order(self):
        for rec in self:
            reference=self.env['stock.picking'].search([('name','=',rec.doc_refrence)],limit=1)
            if reference:
                po=self.env['purchase.order'].search([('name','=',reference.origin)],limit=1)
                if po:
                    rec.purchase_order=po.id
                else:
                    rec.purchase_order=False
            else:
                rec.purchase_order=False


    def _compute_gate_pass(self):
        for rec in self:
            reference=self.env['stock.picking'].search([('name','=',rec.doc_refrence)],limit=1)
            if reference:
                rec.gate_in_id=reference.gate_in_id
            else:
                rec.gate_in_id=False

    @api.depends('line_id')
    def _compute_show_approval(self):
        for rec in self:
            for line in rec.line_id:
                if line.state=='fail':
                    rec.hide_approval = True
                    break
                else:
                    rec.hide_approval = False



    state_approval = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('ready', 'Ready'),
            ('prepare', 'Prepared'),
            ('approve', 'Approved'),
          # New state added
            ('cancel', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        string='Approval Status',
        default='draft',
        tracking=True
    )

    def action_cancel(self):
        for rec in self:
            rec.state_approval='cancelled'


    def sent_approval(self):
        for rec in self:
            if rec.state_approval != 'ready':
                raise UserError("Approval process can only be initiated when the status is 'Ready'.")

            group = self.env.ref('ol_quality_control.group_approve_prepare')
            users_in_group = group.users

            for user in users_in_group:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_model_id': self.env['ir.model']._get('rqi.model').id,
                    'res_id': rec.id,
                    'user_id': user.id,
                    'summary': "Approval for the RQI model",
                    'note': "This record is ready for approval. Please review.",
                    'date_deadline': fields.Datetime.now(),
                })

      
        return True
    @api.onchange("line_id")
    def raiseEror(self):
        for rec in self.line_id:
            if rec.status_qir =='compromised':
                self.state_approval='ready'

    approved = fields.Boolean('Approved')
    unapproved = fields.Boolean('Not approved')
    approval_check=fields.Boolean("Approval Required")
    grn=fields.Many2one("stock.picking","Reference Document")
    mo=fields.Many2one("mrp.production","Reference Document")
    alt_lot_id=fields.Many2one("stock.lot","Alternate Batch Number")
    # ref_type=fields.Char("Refrence Type",compute='compute_reference_type')
    ref_type=fields.Char("Refrence Type")
    doc_id=fields.Integer("Doc ID")
    po=fields.Char("Purchase Order",compute='compute_po')


    @api.depends("grn")
    def compute_po(self):
        for rec in self:
            rec.po= rec.grn.origin if rec.grn.origin else rec.grn.backorder_id.origin
    
    def remove_ready_state(self):
        for rec in self:
            rec.action_prepared()

    @api.constrains('doc_id')
    def update_name(self):
        for rec in self:
            model='mrp.production' if rec.ref_type =="mo" else 'stock.picking'
            record=self.env[model].search([('id','=',rec.doc_id)])
            if record:
                rec.doc_refrence=record.name
                self.compute_reference_type()

    # @api.constrains('doc_refrence')
    def compute_reference_type(self):
        for rec in self:
            if rec.doc_refrence:
                if rec.doc_refrence.startswith('GRN') or rec.doc_refrence.startswith('MTN') or "Draft" in rec.doc_refrence :
                    # rec.ref_type='grn'
                    doc=self.env['stock.picking'].search([('name','=',rec.doc_refrence)])
                    rec.grn=doc.id
                else:
                    # rec.ref_type='mo'
                    doc=self.env['mrp.production'].search([('name','=',rec.doc_refrence)])
                    rec.mo=doc.id
                rec.doc_refrence=doc.name
                rec.lot_id=self.calculate_lots(rec.ref_type,doc)
            else:
                rec.ref_type=False

    def calculate_lots(self,doc_type,document):
        if doc_type =="grn":
            lot_id=document.move_line_ids[0].lot_id if document.move_line_ids else False
        else:
            lot_id=document.lot_producing_id
        if lot_id:
            return lot_id.id
        else:
            return False
        
    

    @api.depends("unapproved",'approved')
    def _compute_approval_required(self):
        for rec in self:
            rec.approval_check = rec.approved or rec.unapproved

    operation_type=fields.Many2one("stock.picking.type",'Operation Type',compute="compute_operation_type")
    operation_type_filter=fields.Char("Operation Type")


    def action_approve(self):
        for rec in self:
            if not rec.approved and not rec.unapproved:
                raise UserError("Document should either be approved or unapproved")
            # if rec.grn:
                # rec.grn.prepare_visibility=True
        res = super(RqiModel, self).action_approve()
    
        return res
    
    def action_reject(self):
        for rec in self:
            if not rec.approved and not rec.unapproved:
                raise UserError("Document should either be approved or unapproved")
            if rec.grn:
                # raise UserError(f"{rec.recent_ids} {rec.grn}")  
                checks=rec.grn.check_ids.filtered(lambda check : check.id in rec.recent_ids)
                for check in checks:
                    self.env['quality.check'].create({
                        'picking_id': rec.grn.id,  
                        'product_id': check.product_id.id,
                        'quality_state': 'none',  
                        'x_studio_purchase_order': check.x_studio_purchase_order,
                        'point_id': check.point_id.id,
                        'title': check.title,
                        'test_type_id': check.test_type_id.id,
                        'measure_on': check.measure_on,
                        'team_id': check.team_id.id,
                        'partner_id': check.partner_id.id,
                        'tolerance_min': check.tolerance_min,
                        'tolerance_max': check.tolerance_max,
                    })
            rec.state_approval='cancel'
        res = super(RqiModel, self).action_reject()
        
        
        return res
    



    def compute_operation_type(self):
        for rec in self:
            if rec.doc_refrence and  rec.doc_refrence.startswith("MO"):
                mo=self.env['mrp.production'].search([('name','=',rec.doc_refrence)])
                if mo:
                    rec.operation_type=mo.picking_type_id.id
                    rec.operation_type_filter=mo.picking_type_id.name
                else:
                    rec.operation_type=False
            else:
                rec.operation_type=False




    @api.onchange('approved')
    def _onchange_approved(self):
        if self.approved:
            self.unapproved = False

    @api.onchange('unapproved')
    def _onchange_unapproved(self):
        if self.unapproved:
            self.approved = False


    def action_measure(self):
        for rec in self:
                for line in rec.line_id:
                    if line.result != 0:
                        line.qc_id['measure'] = line.result
                        # if line.qc_id and line.state=="none":
                        if line.qc_id:
                            line.qc_id.do_measure()
                            if line.state == "pass":
                                line['status_qir'] = 'approve'
                            if line.state == "fail":
                                line['status_qir'] = 'not_approve'
                        else:
                            raise UserError("Record don't Exsists OR Record is not in Draft To Do")
                    else:    
                        raise UserError('Result is not defined')
        # raise UserError(f"=={[line.qc_id.read() for line in self.line_id]}===")
        # raise UserError(f"{self.line_id.filtered(lambda line :line.qc_id.quality_state=='fail').mapped('qc_id').ids}")
        self.recent_ids=list(self.line_id.filtered(lambda line :line.qc_id.quality_state=='fail').mapped('qc_id').ids)
        # raise UserError(self.recent_ids)
        return True