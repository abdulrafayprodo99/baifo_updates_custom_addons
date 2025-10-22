from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime


class deliveryinfo(models.Model):
	_inherit = 'stock.picking'

	driver_name = fields.Char(string='Driver Name')
	mobile_no_driver = fields.Char(string='Mobile No')
	explosive_carrier_no = fields.Char(string='Explosive Vehicle No:')
	vehicle_transport_lic_no = fields.Char(string='Vehicle Transport Licence No')
	holder_of_transport_lic_no = fields.Char(string='Customer Transport Licence No (EL-07)')
	CNIC = fields.Char(string='CNIC')
	date = fields.Date(string='Date')
	date_of_dispatched = fields.Date(string='Date of Dispatch')
	date_of_expected_arival_at_site = fields.Date(string='Date of Expected Arrival at Site')
	no_of_packags = fields.Char(string='No of Packages')

	
