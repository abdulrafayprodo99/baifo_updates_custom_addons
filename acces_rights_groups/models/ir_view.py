from odoo import models, SUPERUSER_ID, _
from odoo.tools.translate import _
import ast
from lxml.builder import E
from odoo.exceptions import UserError


class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'


    def _postprocess_tag_button(self, node, name_manager, node_info):
        # Hide Any Button
        postprocessor = getattr(super(ir_ui_view, self), '_postprocess_tag_button', False)
        if postprocessor:
            super(ir_ui_view, self)._postprocess_tag_button(node, name_manager, node_info)

        hide = None
        hide_button_obj = self.env['approval.view.nodes']
        hide_button_ids = hide_button_obj.sudo().search([('model_id.model','=',name_manager.model._name)])
        # -------------------- Bilal Commit Here For Test Start ---------------------- #
        # for line_ites in hide_button_ids:
        #     uids  = []
        #     for uid in line_ites.user_ids:
        #         uids.append(uid.id)
            
        #     if self._uid in uids:
        #         if line_ites.btn_store_model_nodes_ids.attribute_name == node.get('name'):
        #             node.set('invisible', '0')
        #             if 'attrs' in node.attrib.keys() and node.attrib['attrs']:
        #                 del node.attrib['attrs']
        #             node_info['modifiers']['invisible'] = False
        #         else:
        #             node.set('invisible', '1')
        #             if 'attrs' in node.attrib.keys() and node.attrib['attrs']:
        #                 del node.attrib['attrs']
        #             node_info['modifiers']['invisible'] = True
        # -------------------- Bilal Commit Here For Test End ---------------------- #
        attrs = {'id': node.get('id'), 'select': node.get('select')}
        for line_ites in hide_button_ids:
            field = line_ites.btn_store_model_nodes_ids
            if field:                
                if node.get('groups'):
                    raise UserError('Group hAi')
                    # if the node has a group (e.g. "base.group_no_one")
                    # and the field in the Python model has a group as well (e.g. "base.group_system")
                    # the user must have both group to see the field.
                    # groups="base.group_no_one,base.group_system" directly on the node
                    # would be one of the two groups, not both (OR instead of AND).
                    # To make mandatory to have both groups, wrap the field node in a <t> node with the group
                    # set on the field in the Python model
                    # e.g. <t groups="base.group_system"><field name="foo" groups="base.group_no_one"/></t>
                    # The <t> node will be removed later, in _postprocess_access_rights.
                    node_t = E.t(groups=field.groups, postprocess_added='1')
                    node.getparent().replace(node, node_t)
                    node_t.append(node)
                else:
                    raise UserError('Group nahi hAi')
                            
                    node.set('groups', line_ites.group_id.get_external_id().get(line_ites.group_id.id))

                    # node.set('groups', field.groups)        
        return None
       
        # Filtered with same env user and current model
        # btn_store_model_nodes_ids = hide_button_ids.mapped('btn_store_model_nodes_ids')
        # # translation_obj = self.env['ir.translation']
        # if btn_store_model_nodes_ids:
        #     for btn in btn_store_model_nodes_ids:
        #         if btn.attribute_name == node.get('name'):
        #             hide = [btn]
        #             groups = []
        #             break
        # if hide:
        #     if node.get('groups'):
             
             
        #         node_t = E.t(groups=node.groups, postprocess_added='1')
        #         node.getparent().replace(node, node_t)
        #         node_t.append(node)
        #     else:
        #         node.set('groups', hide.group_id)
        

    
  