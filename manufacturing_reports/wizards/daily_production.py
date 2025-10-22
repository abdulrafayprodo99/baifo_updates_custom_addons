from odoo import models, fields, api
from odoo.exceptions import UserError

from datetime import datetime


class DailyProductionWizard(models.TransientModel):
    _name = 'daily.production.wizard'
    _description = 'Daily Production Wizard'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    current_time = current_datetime.strftime("%H:%M:%S")  # Format: HH:MM:SS

    pdo_id=fields.Many2one('production.demand.plan',"Production Demand Order")
    lot_producing_id = fields.Selection(
        selection=lambda self: self._get_lot_no_selection(),
        string='Lot/Serial Number',
    )
    is_batch_no = fields.Boolean(string='Is Batch Number')

    @api.model
    def _get_lot_no_selection(self):
        # Fetch unique batch_no values from mrp.bom
        mos = self.env['mrp.production'].search([('lot_producing_id', '!=', False)])

        # Use a set to ensure unique batch_no values
        unique_lot_ids = set(mo.lot_producing_id.name for mo in mos)

        # Return as list of tuples for the selection field
        return [(str(lot_producing_id), str(lot_producing_id)) for lot_producing_id in unique_lot_ids]

    def filter(self):
        """Method to filter data from the mrp.production model based on date range and lot_producing_id."""

        # Ensure 'from_date' and 'to_date' are valid
        if self.from_date > self.to_date:
            raise UserError("The 'From Date' cannot be later than the 'To Date'.")

        # Base domain for filtering
        domain = [
            ('create_date', '>=', self.from_date),
            ('create_date', '<=', self.to_date),
            ('pdo_id','=',self.pdo_id.id)
        ]

        # Apply lot_producing_id filter if set
        if self.lot_producing_id:
            domain.append(('lot_producing_id', '=', self.lot_producing_id))

        # Fetch filtered records
        filtered_requirements = self.env['mrp.production'].search(domain)

        return filtered_requirements
    

    def sort_products_by_category(self, products):
        category_order = {
            "Finished Goods": 1,
            "Semi Finished Goods": 2,
            "Work In Process": 3
        }
        
        def get_order(product):
            return category_order.get(product['category_name'], 4)
        
        return sorted(products, key=get_order)

    def prepare_mo_data(self):
        mos = self.filter()

        record_data = {
            "date": self.current_date,
            "time": self.current_time,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "lot_producing_id": self.lot_producing_id,
            "products": {
                "tovex": [],
                "powder": [],
                "accessories": [],
                "thermotube": [],
                "other": [],
            },
            "sub_totals": {
                "tovex": 0,
                "powder": 0,
                "accessories": 0,
                "thermotube": 0,
                "other": 0,
            },
            'is_batch_no': self.is_batch_no,
        }

        sno_counter = 1
        all_products = []  # Collect all products first

        for mo in mos:
            category = mo.product_id.level_3_cat.lower()
            category_name = mo.product_id.level_2_cat.strip() if mo.product_id and mo.product_id.level_2_cat else ""

            # Collect product data
            product_data = {
                "product_name": mo.product_id.name,
                "product_code": mo.product_id.default_code,
                "product_qty": mo.product_qty,
                "unit": mo.product_uom_id.name,
                "lot_no": mo.lot_producing_id.name,
                "category_name": category_name,
                "category" : category,
                'pdo_id': mo.pdo_id.name,
                'doc_type': mo.pdo_id.doc_type,
                'date': mo.date_planned_start,
            }

            all_products.append(product_data)
            sno_counter += 1

        # Sort all collected products before adding them to categories
        sorted_products = self.sort_products_by_category(all_products)

        # Assign sorted products to their respective categories
        for product in sorted_products:
            category = product["category"].lower()

            if "tovex" in category:
                record_data["products"]["tovex"].append(product)
                record_data["sub_totals"]["tovex"] += product["product_qty"]
            elif "powder" in category:
                record_data["products"]["powder"].append(product)
                record_data["sub_totals"]["powder"] += product["product_qty"]
            elif "accessories" in category:
                record_data["products"]["accessories"].append(product)
                record_data["sub_totals"]["accessories"] += product["product_qty"]
            elif "thermotube" in category:
                record_data["products"]["thermotube"].append(product)
                record_data["sub_totals"]["thermotube"] += product["product_qty"]
            else:
                record_data["products"]["other"].append(product)
                record_data["sub_totals"]["other"] += product["product_qty"]

        # raise UserError(str(record_data))  # Debugging check
        

        return record_data

    def generate_report(self):
        # Add logic to generate the Daily production report
        report_data = self.prepare_mo_data()
        report_data.get("report")
        return self.env.ref('manufacturing_reports.action_daily_production_pdf').report_action(
         self, data={'report_data': report_data})



