# from odoo import models, fields, api
# from datetime import date
# from odoo.exceptions import UserError

# class MrpBom(models.Model):
#     _inherit = 'mrp.bom'

#     batch_no = fields.Char(string='Fiscal Year')
#     effective_date = fields.Date(string='Effective Date')
#     end_date = fields.Date(string='End Date')

#     readonly_check = fields.Boolean(default=False,compute='_onchange_state',store=True)
    
#     state = fields.Selection([
#         ('not_approved', 'Not Approved'),
#         ('approved', 'Approved'),
#     ], default='not_approved', string="Status")

#     @api.depends('state')
#     def _onchange_state(self):
#         for rec in self:
#             if rec.state == 'approved':
#                 rec.readonly_check = True  
#             else:
#                 rec.readonly_check = False


#     def action_approve(self):
#         for record in self:
#             record.state = 'approved'

#     def action_disapprove(self):
#         for record in self:
#             record.state = 'not_approved'

#     @api.model
#     def create(self, vals):
#         # Ensure 'product_tmpl_id' is provided in the creation values
#         product_tmpl_id = vals.get('product_tmpl_id')
#         if product_tmpl_id:
#             # Search for existing BOMs for the product
#             existing_boms = self.search([('product_tmpl_id', '=', product_tmpl_id)])
#             for bom in existing_boms:
#                 # Check the conditions: effective_date and state
#                 if bom.end_date and bom.end_date < date.today():
#                     continue  # This BOM meets the requirements, allow creation
#                 else:
#                     raise UserError(
#                         "A BOM already exists for this product. Please end the existing BOM(s)."
#                     )
#         # If no conflicting BOMs, proceed with creation
#         return super(MrpBom, self).create(vals)
    

#     # def write(self, vals):
#     #     # Check if 'product_tmpl_id' is being updated
#     #     product_tmpl_id = vals.get('product_tmpl_id')
#     #     if product_tmpl_id or 'end_date' in vals:
#     #         # Use the current product_tmpl_id if not being updated
#     #         for record in self:
#     #             current_product_tmpl_id = product_tmpl_id or record.product_tmpl_id.id
#     #             # Search for other BOMs with the same product template ID
#     #             existing_boms = self.search([('product_tmpl_id', '=', current_product_tmpl_id), ('id', '!=', record.id)])
#     #             for bom in existing_boms:
#     #                 # Check the conditions: end_date
#     #                 if bom.end_date and bom.end_date < date.today():
#     #                     continue  # This BOM meets the requirements, allow update
#     #                 else:
#     #                     raise UserError(
#     #                         "A BOM already exists for this product. Please end the existing BOM(s) before updating."
#     #                     )
#     #     # If no conflicting BOMs, proceed with the update
#     #     return super(MrpBom, self).write(vals)




from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _, Command

class MrpBom(models.Model):
    _inherit = 'mrp.bom'


    def _get_year_selection(self):
        current_year = datetime.now().year
        years = [(year, str(year)) for year in range(current_year - 10, current_year + 1)]
        return years

    # batch_no = fields.Selection(selection=_get_year_selection, string="Year", required=True, default=lambda self: datetime.now().year)




    # M Azeem Task: 43167
    batch_no = fields.Selection([
        ('2014-2015','2014-2015'),  ('2015-2016','2015-2016'), ('2016-2017','2016-2017'),
        ('2017-2018','2017-2018'),  ('2018-2019','2018-2019'), ('2019-2020','2019-2020'),
        ('2020-2021','2020-2021'),  ('2021-2022','2021-2022'), ('2022-2023','2022-2023'),
        ('2023-2024','2023-2024'),  ('2024-2025','2024-2025'), ('2025-2026','2025-2026'),
        ('2026-2027','2026-2027'),  ('2027-2028','2027-2028'), ('2028-2029','2028-2029'),
        ('2029-2030','2029-2030'),  ('2030-2031','2030-2031'), ('2031-2032','2031-2032'),
        ('2032-2033','2032-2033'),  ('2033-2034','2033-2034')
    ], string="Fiscal Year", required=True)




    #batch_no = fields.Char(string='Fiscal Year')
    effective_date = fields.Date(string='Effective Date')
    end_date = fields.Date(string='End Date')

    readonly_check = fields.Boolean(default=False, compute='_onchange_state', store=True)
    
    state = fields.Selection([
        ('not_approved', 'Not Approved'),
        ('approved', 'Approved'),
    ], default='not_approved', string="Status")
    
    sequence = fields.Char(string="BOM Sequence", readonly=True)
    code = fields.Char('BOM Version')

    total_cost = fields.Float(
        string="Total Cost", compute="_compute_total_cost", store=True
    )
    standard_rate = fields.Float(
        string="Standard Rate", compute="_compute_standard_rate", store=True
    )


    state_display = fields.Char(
        string="Status", compute="_compute_state_display", store=True
    )


    bom_version_id = fields.Integer(string="BOM Version ID")

        # Remove the SQL constraint from the list
    _sql_constraints = []

    # @api.constrains('bom_version_id')
    # def _check_bom_version_length(self):
    #     for record in self:
    #         if record.bom_version_id and len(str(record.bom_version_id)) > 4:
    #             raise ValidationError("BOM Version ID must not exceed 4 digits.")

    # @api.depends('sequence', 'code')
    # def _compute_bom_version_id(self):
    #     for record in self:
    #         if record.code:
    #             # Count existing records with the same code
    #             existing_count = self.search_count([('code', '=', record.code)])
    #             new_sequence = f"{existing_count + 1:04d}"  # Generate padded number (0001, 0002, etc.)
    #             record.bom_version_id = f"{record.code} - {new_sequence}"
    #         else:
    #             record.bom_version_id = ''



    @api.depends('state')
    def _compute_state_display(self):
        """Compute the state as a char field."""
        for record in self:
            record.state_display = dict(self._fields['state'].selection).get(record.state, record.state)

    @api.depends('bom_line_ids.total_cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = sum(record.bom_line_ids.mapped('total_cost'))

    @api.depends('total_cost', 'product_qty')
    def _compute_standard_rate(self):
        for record in self:
            record.standard_rate = record.total_cost / record.product_qty if record.product_qty else 0.0


    @api.depends('state')
    def _onchange_state(self):
        for rec in self:
            if rec.state == 'approved':
                rec.readonly_check = True  
            else:
                rec.readonly_check = False

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_disapprove(self):
        for record in self:
            record.state = 'not_approved'






    @api.model
    def create(self, vals):
        # Mapping technical field names to custom labels
        field_labels = {
            'effective_date': "Effective Date",
            'batch_no': "Fiscal Year",
            'code': "BOM Version",
            'bom_version_id': "BOM Version Id",
            'end_date': "End Date",
        }

        # Determine required fields based on conditions
        required_fields = ['effective_date', 'batch_no']

        if vals.get('effective_date') and vals.get('end_date'):
            # If both 'effective_date' and 'end_date' exist, 'code' and 'bom_version_id' are NOT required
            pass
        elif vals.get('effective_date') and not vals.get('end_date'):
            # If only 'effective_date' is provided, 'code' and 'bom_version_id' are required
            required_fields.extend(['code', 'bom_version_id'])

        # Validate required fields
        missing_fields = [field_labels[field] for field in required_fields if not vals.get(field)]
        if missing_fields:
            raise UserError(_("The following fields are required: %s") % ", ".join(missing_fields))

        # Generate the sequence number
        current_year = date.today().year
        bom_count = self.search_count([('create_date', '>=', f'{current_year}-01-01')]) + 1
        vals['sequence'] = f"BOM-{current_year}-{bom_count:04d}"

        # Ensure unique bom_version_id per code if 'code' is provided
        if vals.get('code'):
            existing_bom = self.search([('code', '=', vals['code'])], order="bom_version_id desc", limit=1)
            vals['bom_version_id'] = existing_bom.bom_version_id + 1 if existing_bom else 1

        return super(MrpBom, self).create(vals)






    # def copy(self, default=None):
    #     default = dict(default or {})

    #     # Get duplicated data without saving
    #     copied_values = self._copy_data(default)
    #     res = self.new(copied_values)  # Create an unsaved record

    #     raise UserError("Copy")

    #     # if self.operation_ids:
    #     #     operations_mapping = {}
    #     #     for original, copied in zip(self.operation_ids, res.operation_ids.sorted()):
    #     #         operations_mapping[original] = copied

    #     #     for bom_line in res.bom_line_ids:
    #     #         if bom_line.operation_id:
    #     #             bom_line.operation_id = operations_mapping.get(bom_line.operation_id)

    #     #     for operation in self.operation_ids:
    #     #         if operation.blocked_by_operation_ids:
    #     #             copied_operation = operations_mapping.get(operation)
    #     #             if copied_operation:
    #     #                 dependencies = [
    #     #                     Command.link(operations_mapping[dependency].id)
    #     #                     for dependency in operation.blocked_by_operation_ids
    #     #                     if dependency in operations_mapping
    #     #                 ]
    #     #                 copied_operation.blocked_by_operation_ids = dependencies

    #     return res

    # def copy(self, default=None):
    #     self.ensure_one()
    #     default = default or {}

    #     # # Prepare default values without saving
    #     # default_values = {field: self[field] for field in self._fields if self._fields[field].store}

    #     # # Modify default values if needed (e.g., change name)
    #     # default_values['code'] = f"Copy of {self.code}" if self.code else "Copy"

    #     return {
    #         'name': 'Duplicate Bill of Materials',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'mrp.bom',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'context': {'default_code' : "PC"},
    #         'target': 'current',
    #     }


    def action_copy(self):
        self.ensure_one()
        
        # Default values without saving the new record
        default_values = {
            'default_code': f"Copy of {self.code}" if self.code else "PC",
            'default_product_tmpl_id': self.product_tmpl_id.id,
            'default_product_qty': self.product_qty,
            'default_bom_version_id': self.bom_version_id,
            'default_bom_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty
            }) for line in self.bom_line_ids],
        }

        return {
            'name': 'Duplicate Bill of Materials',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'view_type': 'form',
            'context': default_values,
            'target': 'current',
        }

    