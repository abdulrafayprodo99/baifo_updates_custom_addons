# # -*- coding: utf-8 -*-
# from odoo import api, fields, models,_
# from odoo.exceptions import UserError

# class CustomerLicense(models.Model):
#     _name = "customer.license"
#     _description = "Customer License Model"

#     name= fields.Char(string="Name")
#     customer_code_old= fields.Char(string="Customer Code Old")
#     customer_code_new= fields.Char(string="Customer Code New")
#     customer_name =fields.Many2one('res.partner',string='Customer')
#     validity_from = fields.Date(string="Validity From")
#     validity_to = fields.Date(string="Validity To")

#     def name_get(self):
#         result = []
#         for rec in self:
#             result.append((rec.id, '%s [ %s - %s ]' % (rec.name,rec.validity_from,rec.validity_to)))
#         return result


#     @api.onchange('customer_name')
#     def update_codes(self):
#      if self.customer_name:
#       self['customer_code_old'] = self.customer_name.x_studio_existing_code
#       self['customer_code_new'] = self.customer_name.x_studio_new_code
    
#     def update(self):
        
#         current = []
#         if self.customer_name:
#             search = self.env['res.partner'].search([('id','=',self.customer_name.id)])
#             # search['customer_license_id'] = self 
#             for i in search.customer_license_id:
#                 current.append(i.id)
#             current.append(self.id)
#             searchs = self.env['customer.license'].search([('id','in',current)])

#             # searchs.append(self)
#             search['customer_license_id'] = searchs 
#             # raise UserError(str(self) + "///" + str(searchs))



# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CustomerLicense(models.Model):
    _name = "customer.license"
    _description = "Customer License Model"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Add mail.thread and mail.activity.mixin

    name = fields.Char(string="Name")
    customer_code_old = fields.Char(string="Customer Code Old")
    customer_code_new = fields.Char(string="Customer Code New")
    customer_name = fields.Many2one('res.partner', string='Customer')
    validity_from = fields.Date(string="Validity From")
    validity_to = fields.Date(string="Validity To")

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s [ %s - %s ]' % (rec.name, rec.validity_from, rec.validity_to)))
        return result

    @api.onchange('customer_name')
    def update_codes(self):
        if self.customer_name:
            self.customer_code_old = self.customer_name.x_studio_existing_code
            self.customer_code_new = self.customer_name.x_studio_new_code
            if self._origin:
                self._origin.message_post(body=_("Updated codes for customer %s: Old Code - %s, New Code - %s" % 
                                     (self.customer_name.name, self.customer_code_old, self.customer_code_new)),message_type='comment')

    def update(self):
        current = []
        if self.customer_name:
            search = self.env['res.partner'].search([('id', '=', self.customer_name.id)])
            if not search:
                raise UserError(_("No partner found with the provided ID."))
            
            for i in search.customer_license_id:
                current.append(i.id)
            current.append(self.id)
            searchs = self.env['customer.license'].search([('id', 'in', current)])
            
            search.customer_license_id = searchs
            self.message_post(body=_("Updated customer licenses for partner %s: Added license IDs - %s" % 
                                     (self.customer_name.name, current)))

    @api.model
    def create(self, vals):
        record = super(CustomerLicense, self).create(vals)
        record.message_post(body=_("Created new customer license: %s" % record.name))
        return record

    def write(self, vals):
        result = super(CustomerLicense, self).write(vals)
        self.message_post(body=_("Updated customer license ID %s with values: %s" % (self.id, vals)))
        return result

    def unlink(self):
        for record in self:
            record.message_post(body=_("Deleting customer license ID %s with name %s" % (record.id, record.name)))
        return super(CustomerLicense, self).unlink()
