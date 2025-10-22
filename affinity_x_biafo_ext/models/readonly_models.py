from odoo import models, SUPERUSER_ID, _, api
from odoo.tools.translate import _
import ast
from odoo.exceptions import UserError
from lxml import etree
import  json

class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'

    # def _postprocess_tag_field(self, node, name_manager, node_info):
    #     try:
    #         res = super()._postprocess_tag_field(node, name_manager, node_info)
    #         hide_field_obj = self.env['purchase.request'].sudo().search([])
    #         for hide_field in hide_field_obj:
    #             if node.tag == 'field' or node.tag == 'label' :
    #                 if hide_field.readonly_check:
    #                     # if 'readonly' in node_info['modifiers'] and isinstance(node_info['modifiers']['readonly'], list):
    #                     #     # TODO combine with AND or OR, use implicit AND for now.
    #                     #     node_info['modifiers']['readonly'].append(('readonly_check', '=', True))
    #                     # else:
    #                     #     node_info['modifiers']['readonly'] = [('readonly_check', '=', True)]

    #                     node_info['modifiers']['readonly'] = [('readonly_check', '=', True)]
                        
    #                     if node.get('name') == "readonly_check":
    #                         node_info['modifiers']['readonly'] = False
    #                     return 
            
    #     except Exception as e:
    #         pass
    #     return super()._postprocess_tag_field(node, name_manager, node_info)
    
   