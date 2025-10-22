from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime


APPROVAL_STATES = [
   ('prepare','Prepared'),
   ('approve','Approved'),
   ('cancel','Cancelled'),
   
]

class RQIMODEL(models.Model):
    _name="rqi.model"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    state_approval = fields.Selection(selection=APPROVAL_STATES,string="Approval Status", tracking=True,copy=False) 
    name = fields.Char(string='Name', required=True)
    team_id = fields.Many2one('quality.alert.team',string="QR Type" , readonly=True)
    date = fields.Date(string='QIR Date',)
    doc_refrence = fields.Char(string='Document Refrence', readonly=True)
    doc_date = fields.Date(string='Document Date', readonly=True)
    product_id = fields.Many2one("product.product",string="Item Name", readonly=True)
    partner_id = fields.Many2one("res.partner",string="Supplier")
    sample = fields.Char(string="Sample #" )
    lot_id = fields.Many2one('stock.lot',string="Batch #", readonly=True)
    note = fields.Text(string="Justification")

    prepared_by = fields.Many2one('res.users', string="Prepared By",readonly=True)
    verified_by = fields.Many2one('res.users', string="Verified By",readonly=True)
    approved_by = fields.Many2one('res.users', string="Approved By",readonly=True)

    prepared_by_timestamp = fields.Datetime(string="Prepared Timestamp",readonly=True,copy=False)
    verified_by_timestamp = fields.Datetime(string="Verified Timestamp",readonly=True,copy=False)
    approved_by_timestamp = fields.Datetime(string="Approved Timestamp",readonly=True,copy=False)




    line_id = fields.One2many("rqi.model.line",'rqi_id', string="RQI Lines")

    reject_note = fields.Text(string="Rejection Note")

    def action_measure(self):
        for rec in self:
            # if rec['state_approval'] == 'approve':
                for line in rec.line_id:
                    if line.result != 0:
                        line.qc_id['measure'] = line.result
                        if line.qc_id and line.state=="none":
                            line.qc_id.do_measure()
                            if line.state == "pass":
                                line['status_qir'] = 'approve'
                            if line.state == "fail":
                                line['status_qir'] = 'not_approve'
                        else:
                            raise UserError("Record don't Exsists OR Record is not in Draft To Do")
                    else:    
                        raise UserError('Result is not defined')
            # else:
            #     raise UserError('Please Approved this Record ')
                
    def action_prepared(self):
       self['state_approval'] = 'prepare'
       self['prepared_by'] = self.write_uid.id
       self['prepared_by_timestamp'] = fields.Datetime.now()
       
    
    def action_approve(self):
        self['state_approval']= 'approve'
        self['approved_by'] = self.write_uid.id
        self['approved_by_timestamp'] = fields.Datetime.now()
        picking= self.env['stock.picking'].search([('origin','=', self.doc_refrence)])
        mrp = self.env['mrp.production'].search([('origin','=', self.doc_refrence)])
        for pick in picking:
            pick.action_verify()
        for m in mrp:
            m.action_verify()


    

    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'rqi.model',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        

   

class RQIMODELLINE(models.Model):
    _name="rqi.model.line"

    rqi_id = fields.Many2one('rqi.model',string="RQI")
    point_id = fields.Many2one('quality.point',string="Code" , readonly=True)
    quality_title = fields.Char('Quality Perameter',related="point_id.title" )
    standards = fields.Char(string="Standards" , readonly=True)
    result = fields.Char(string="Actual Result")
    remarks = fields.Char(string="Remarks")
    status = fields.Selection(selection=[('none','None'),('pass','Pass'),('fail','Fail')])
    fail_type = fields.Selection(selection=[('discard','Discard / Disposed'),('rtn_supplier','Return To Supplier')])
    qc_id = fields.Many2one('quality.check', string="QC ID")
    state = fields.Selection(related="qc_id.quality_state", string="QIC Status")
    status_qir  = fields.Selection(selection=[('approve','Approve'),('not_approve','Not Approve'),('compromised','Compromised')],string="Status")

class STOCKPICKING(models.Model):
    _inherit = 'stock.picking'

    def action_prepare(self):
        res = super(STOCKPICKING, self).action_prepare()
       
        key_detail = ''
        result_dict = {}
        if self:
            # ('x_studio_purchase_order','=',self.origin),
            qc = self.env['quality.check'].search([('picking_id','=',self.id)])

            if qc:
                for rec in qc:
                    if rec['x_studio_purchase_order']:
                        key = rec['x_studio_purchase_order'] + ','+str(rec['product_id']['id']) + ',' + str(rec['team_id']['id']) + ',' +str(rec['partner_id']['id'])
                    else:
                        key = self['name'] + ','+str(rec['product_id']['id']) + ',' + str(rec['team_id']['id']) + ',' + str(0)
                    if key not in result_dict:
                        result_dict[key] = []
                        if rec not in result_dict[key]: 
                            result_dict[key].append(rec)
                
                    if rec not in result_dict[key]:
                        result_dict[key].append(rec)
                    
                # raise UserError(str(result_dict))
                for keys, items in result_dict.items():
                    lines_data = [] 
                    for line in items:
                        min = round(line['tolerance_min'],2)
                        max = round(line['tolerance_max'],2)
                        measure = round(line['measure'],2)
                        lines_data.append((0,0,{
                        'point_id': line['point_id']['id'],
                        'quality_title': line['point_id'].title,
                        'standards' : str(min) +' '+ '-' +' '+ str(max),
                        'result': str(measure),
                        'qc_id' : line['id'],
                        }))
            
                    split_data = keys.split(',')
                    # raise UserError(key_detail)
                    purchase_order = self.env['purchase.order'].search([('name','=',split_data[0])])
                    qir = self.env['rqi.model'].create({
                        'name': self.env['ir.sequence'].next_by_code('qir.sequence'),
                        'product_id': int(split_data[1]),
                        'partner_id': int(split_data[3]) if int(split_data[3]) != 0 else False,
                        'team_id': int(split_data[2]),
                        'lot_id': False,
                        'line_id':lines_data,
                        'doc_refrence': split_data[0],
                        'doc_date': purchase_order.date_order.date() if purchase_order else datetime.today(),
                        'date': datetime.now(),
                    })
                    if qir :
                        qir.action_prepared()
        return res


    def action_verify(self):
        res = super(STOCKPICKING, self).action_verify()

        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        if self.picking_type_id.is_grn_approval  == True:
            qc = self.env['quality.check'].search([('x_studio_purchase_order','=',self.origin),('picking_id','=',self.id)])
            # raise UserError("s")
            for q in qc:
                if q.quality_state != "none":
                    return res
                # else:
                #     raise UserError("Please Check Related QC")

    def action_reject(self):
        res = super(STOCKPICKING, self).action_reject()

        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        if self.picking_type_id.is_grn_approval  == True:
            qc = self.env['rqi.model'].search([('doc_refrence','=',self.origin)])
            if qc:
                qc['state_approval'] = 'cancel'
        return res
    
    
        
class MrpPrduction(models.Model):
    _inherit = 'mrp.production'
    
    
    def action_checked(self):
        res = super(MrpPrduction, self).action_checked()
        for rec in self:
            key_detail = ''
            result_dict = {}
            qc = self.env['quality.check'].search([('production_id','=',self.id)])

            if qc:
                for rec in qc:
                    key = self['name'] + ','+str(rec['product_id']['id']) + ',' + str(rec['team_id']['id']) 
                    if key not in result_dict:
                        result_dict[key] = []
                        if rec not in result_dict[key]: 
                            result_dict[key].append(rec)
                
                    if rec not in result_dict[key]:
                        result_dict[key].append(rec)
                    
                # raise UserError(str(result_dict))
                for keys, items in result_dict.items():
                    lines_data = [] 
                    for line in items:
                        min = round(line['tolerance_min'],2)
                        max = round(line['tolerance_max'],2)
                        measure = round(line['measure'],2)
                        lines_data.append((0,0,{
                        'point_id': line['point_id']['id'],
                        'quality_title': line['point_id'].title,
                        'standards' : str(min) +' '+ '-' +' '+ str(max),
                        'result': str(measure),
                        'qc_id' : line['id'],
                        }))
            
                    split_data = keys.split(',')
                    # raise UserError(key_detail)
                    production = self.env['mrp.production'].search([('name','=',split_data[0])])
                    if not self.env['rqi.model'].search([('mo','=',self.id)]):
                        qir = self.env['rqi.model'].create({
                            'name': self.env['ir.sequence'].next_by_code('qir.sequence'),
                            'product_id': int(split_data[1]),
                            'partner_id': False,
                            'team_id': int(split_data[2]),
                            'lot_id': False,
                            'line_id':lines_data,
                            'doc_refrence': split_data[0],
                            # 'doc_date': production.date_planned_start.date(),
                            'date': datetime.now(),
                        })
                        if qir :
                            qir.action_prepared()
        return res
    
    
    
    def action_verify(self):
        res = super(MrpPrduction, self).action_verify()

        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        if self.picking_type_id.is_grn_approval  == True:
            qc = self.env['quality.check'].search([('x_studio_purchase_order','=',self.name)])
            # raise UserError("s")
            for q in qc:
                if q.quality_state != "none":
                    return res
                else:
                    raise UserError("Please Check Related QC")
    
    def action_reject(self):
        res = super(MrpPrduction, self).action_reject()

        # if self.picking_type_id.id in  [1,10,11,23,24,22,6,37,14]:
        if self.picking_type_id.is_grn_approval  == True:
            qc = self.env['rqi.model'].search([('doc_refrence','=',self.name)])
            if qc:
                qc['state_approval'] = 'cancel'
        return res