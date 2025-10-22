# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Iso(models.Model):
    _name = "iso"
    _description = "ISO"

    name= fields.Char(string="Name")
    iso_number= fields.Char(string="ISO Number")
