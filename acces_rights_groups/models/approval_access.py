from odoo import fields,models,api,_
from odoo.tools.translate import TranslationModuleReader
from lxml import etree
from odoo.exceptions import UserError


class ApprovalsAccess(models.Model):
    _name = 'approval.access'
    _description = 'Approval Access'
    
    name = fields.Char('Name')
    model_id = fields.Many2one(
        'ir.model', string='Model', index=True, required=True, ondelete='cascade')
    line_ids = fields.One2many('approval.view.nodes','approval_id','Line Ids')


class approval_view_nodes(models.Model):
    _name = 'approval.view.nodes'
    _description = 'Hide View Nodes'

    approval_id = fields.Many2one('approval.access')
    model_id = fields.Many2one(
        'ir.model', string='Model', related="approval_id.model_id", index=True, required=True, ondelete='cascade')

    model_name = fields.Char(string='Model Name', related='model_id.model', readonly=True, store=True)
    
    btn_store_model_nodes_ids = fields.Many2one('approval.store.nodes',string='Hide Button',domain="[('node_option','=','button')]")
    group_id = fields.Many2one(comodel_name="res.groups", string="User Groups", required=True)
    
    user_ids = fields.Many2many('res.users', 'approval_button_users_rel_ah', 'view_node_id', 'user_id', 'Users')

    def _store_btn_data(self,btn, smart_button=False,smart_button_string=False):
        # string_value is used in case of kanban view button store, 
        string_value = 'string_value' in self._context.keys() and self._context['string_value'] or False
        
        store_model_button_obj = self.env['approval.store.nodes']
        name = btn.get('string') or string_value
        if smart_button:
            name = smart_button_string
        # raise UserError(str(btn.get('groups')))
        store_model_button_obj.create({
                'model_id' : self.model_id.id,
                'node_option' : 'button',
                'attribute_name' : btn.get('name'),
                'attribute_string' : name,
                'button_type' : btn.get('type'),
                'is_smart_button' : smart_button,
                'lang_code':self.env.lang,
                'groups': tuple(tuple(n.get('groups').split(',')) for n in etree.XML(res['arch']).xpath('ancestor-or-self::*[@groups]')),
                
            })
       

    
    @api.model
    @api.onchange('model_id')
    def _get_button(self):
        store_model_nodes_obj = self.env['approval.store.nodes']
        view_obj = self.env['ir.ui.view']

        if self.model_id and self.model_name:
            

            view_list = ['form']
            for view in view_list:
                for views in view_obj.search([('model','=',self.model_name),('type','=',view)]):
                    res = self.env[self.model_name].sudo().get_view(view_id=views.id,view_type=view)
                    # res = self.env[self.model_name].sudo().fields_view_get(view_id=views.id,view_type=view)
                    doc = etree.XML(res['arch'])

                    object_button = doc.xpath("//button[@type='object']")
                    for btn in object_button:
                        string_value = btn.get('string')
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text if not btn.text.startswith('\n') else False
                            except:
                                pass
                        if btn.get('name') and string_value:
                            domain = [('button_type','=',btn.get('type')),('attribute_string','=',string_value),('attribute_name','=',btn.get('name')),('model_id','=',self.model_id.id),('node_option','=','button')]
                            if not store_model_nodes_obj.search(domain):
                                self.with_context(string_value=string_value)._store_btn_data(btn)
   

class store_model_nodes(models.Model):
    _name = 'approval.store.nodes'
    _description = 'Store Model Nodes'
    _rec_name = 'attribute_string'

    
    model_id = fields.Many2one('ir.model', string='Model', index=True, ondelete='cascade',required=True)
    node_option = fields.Selection([('button','Button'),('page','Page'),('link','Link')],string="Node Option",required=True)
    attribute_name = fields.Char('Attribute Name')
    attribute_string= fields.Char('Attribute String',required=True,translate=True)
    lang_code = fields.Char("Language Code")
    button_type = fields.Selection([('object','Object'),('action','Action')],string="Button Type")
    is_smart_button = fields.Boolean('Smart Button')
    groups = fields.Char('groups')
    

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res_ids = super(store_model_nodes, self).create(vals_list)
    #     res_ids.write()
    #     return res_ids

    def name_get(self):
        result = []
        for rec in self:
            name = rec.attribute_string
            if rec.attribute_name:
                name = name +' (' + rec.attribute_name + ')'
                if rec.is_smart_button and rec.node_option == 'button':
                   name = name + ' (Smart Button)'
            result.append((rec.id, name))
        return result

    