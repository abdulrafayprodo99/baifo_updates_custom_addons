from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime
class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'
    
    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        purchase = False

        for item in self.item_ids:
            line = item.line_id

            # Ataib Start
            linked_po_lines = self.env['purchase.order.line'].search([
                ('purchase_request_lines', 'in', line.id),
                ('state', 'not in', ['cancel'])
            ])

            existing_po_qty = sum(
                pol.product_uom._compute_quantity(pol.product_qty, line.product_uom_id)
                for pol in linked_po_lines
            )

            requested_qty = item.product_uom_id._compute_quantity(item.product_qty, line.product_uom_id)

            # Rao Abdul Rehman (commented this code)
            # if existing_po_qty + requested_qty > line.product_qty:
            #     raise UserError(_(
            #         'Cannot proceed. RFQ quantity for product "%s" exceeds the Purchase Request total.\n'
            #         'Requested: %s, Existing in RFQs: %s, Total in PR: %s'
            #     ) % (
            #         line.product_id.display_name,
            #         requested_qty,
            #         existing_po_qty,
            #         line.product_qty
            #     ))
            # Rao Abdul Rehman (commented this code)
            

            # Ataib End

            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin,
                    line.request_id
                )
                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            # If Unit of Measure is not set, update from wizard.
            if not line.product_uom_id:
                line.product_uom_id = item.product_uom_id
            # Allocation UoM has to be the same as PR line UoM
            alloc_uom = line.product_uom_id
            wizard_uom = item.product_uom_id
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            else:
                po_line_data = self._prepare_purchase_order_line(purchase, item)
                if item.keep_description:
                    po_line_data["name"] = item.name
                po_line = po_line_obj.create(po_line_data)
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            # TODO: Check propagate_uom compatibility:
            new_qty = pr_line_obj._calc_new_qty(
                line, po_line=po_line, new_pr_line=new_pr_line
            )
            po_line.product_qty = new_qty
            # The quantity update triggers a compute method that alters the
            # unit price (which is what we want, to honor graduate pricing)
            # but also the scheduled date which is what we don't want.
            date_required = item.line_id.date_required
            po_line.date_planned = datetime(
                date_required.year, date_required.month, date_required.day
            )
            res.append(purchase.id)
            if item.line_id.request_id and item.line_id.request_id.line_ids:
                for line in item.line_id.request_id.line_ids:
                    if line.product_id == item.line_id.product_id and purchase.id not in line.po_ids.ids:
                        line.po_ids = [(4, purchase.id)]

        # M Azeem started Task 43173
        pr_active_id = self.env.context.get('active_id')
        pr_record = self.env['purchase.request'].browse(pr_active_id)
        if pr_record.pr_type == 'opex' and pr_record.opex_type == 'production':
            group_name = 'pr.After_Approved_Group'
            summary='Request is Approved State'
        elif pr_record.pr_type  == 'opex' and pr_record.opex_type == 'consumable' and pr_record.opex_sub_type == 'plant':
            group_name = 'pr.After_Approved_Group'
            summary='Request is Approved State'
        elif pr_record.pr_type == 'opex' and pr_record.opex_type == 'consumable' and pr_record.opex_sub_type == 'head_office': 
            group_name = 'pr.After_Approved_Group'
            summary='Request is Approved State'
        elif pr_record.pr_type == 'capex' and pr_record.capex_type == 'plant': 
            group_name = 'pr.After_Approved_Group'
            summary='Request is Approved State'
        elif pr_record.pr_type == 'capex' and pr_record.capex_type == 'head_office': 
            group_name = 'pr.After_Approved_Group'
            summary='Request is Approved State'
            
        group = self.env.ref(group_name)

        # raise UserError(f"{self.env.user.id} {group.users.ids}")
        if self.env.user.id in group.users.ids:

            # Search for specific activities related to this purchase request
            activities = self.env['mail.activity'].search([
                ('res_model', '=', "purchase.request"),  # Related to the purchase request model
                ('res_id', '=', self.id),  # For this specific request
                ('user_id', 'in', group.users.ids),  # For users in the group2
                ('summary', '=', summary)  # Match specific activity created in action_prepared
            ])
            
            # Unlink the matched activities
            if activities:
                activities.unlink()
        # M Azeem ended
            

        return {
            "domain": [("id", "in", res)], 
            "name": _("RFQ"),
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }