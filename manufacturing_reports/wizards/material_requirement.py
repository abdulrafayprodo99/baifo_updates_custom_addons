from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
from datetime import timedelta



class MaterialRequirementWizard(models.TransientModel):
    _name = 'material.requirement.wizard'
    _description = 'Material Requirement Wizard'

    # product_id = fields.Many2one('product.product', string='Product', required=True)
    # quantity = fields.Float(string='Quantity', required=True)


    # from_date = fields.Date(string='From Date', required=True)
    # to_date = fields.Date(string='To Date', required=True)

    current_datetime = datetime.now()
    current_datetime+=timedelta(hours=5)
    current_date = current_datetime.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    current_time = current_datetime.strftime("%H:%M:%S")  # Format: HH:MM:SS

    material_id=fields.Many2many(comodel_name="affinity.material.requirement",string='Production Planning')





    def filter_material_data(self):
        """Method to filter data from the affinity.material.requirement model based on date range."""
        # Ensure 'from_date' and 'to_date' are valid
        # if self.from_date > self.to_date:
        #     raise UserError("The 'From Date' cannot be later than the 'To Date'.")

        # Fetch data from affinity.material.requirement model based on date range
        filtered_requirements = self.env['affinity.material.requirement'].search([
            # ('date_from', '>=', self.from_date),
            # ('date_to', '<=', self.to_date)
            ('id', 'in', self.material_id.ids)
        ])
        # filtered_requirements.filtered(lambda material : material.id in lst(self.material_id.ids))
        
        return filtered_requirements





    def prepare_material_data(self):
        """Method to prepare data in the required format."""
        
        # Fetch the material requirement records based on date range
        material_reqs = self.filter_material_data()
        
        # Prepare the structured data
        material_data = []
        grand_total = 0
        
        for rec in material_reqs:
            record_data = {
                "name": rec.name,
                "date_from": "",
                "date_to": "",
                "lines": {
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
                "total": 0
            }
            
            # Incremental counter for S.no.
            sno_counter = 1
            
            # Categorize the material demand lines
            for line in rec.material_demand_line_ids:
                category = line.product_id.level_3_cat.lower() if line.product_id.level_3_cat else ""
                # raise UserError(line.pdo_id.doc_type)

                line_data = {
                    "s.no.": sno_counter,
                    "pdo_id": getattr(line.pdo_id, "name", "N/A"),
                    "doc_type": getattr(line.pdo_id, "doc_type", "N/A"),
                    "customer": getattr(line.customer_id, "name", "N/A"),
                    "unit": getattr(line.product_id.uom_id, "name", "N/A"),
                    "sale_order_no": getattr(line.sale_order_id, "name", "N/A"),
                    "product": getattr(line.product_id, "name", "N/A"),
                    "product_code": getattr(line.product_id, "default_code", "N/A"),
                    "qty": getattr(line, "product_demand_quantity", 0),
                    "mo_qty": getattr(line, "mo_qty", 0),
                    "remaining_qty": getattr(line, "remaining_qty", 0),
                    "process_qty": getattr(line, "process_qty", 0),
                    # "date_from": getattr(line, "scheduled_date", "N/A"),
                    "date_from": line.scheduled_date.strftime('%d/%m/%Y') if line.scheduled_date else "N/A",
                    # "date_to": getattr(rec, "production_end_date", "N/A"),
                    # "date_to": getattr(line, "production_end_date", "N/A"),
                    "date_to":line.production_end_date.strftime('%d/%m/%Y') if line.production_end_date else "N/A",
                    # "dispatch_date": getattr(line, "dispatch_date", "N/A"),
                    "dispatch_date": line.scheduled_date.strftime('%d/%m/%Y') if line.scheduled_date else "N/A",
                    "remarks": getattr(line, "x_studio_remarks", "N/A"),
                }


                
                if 'tovex' in category:
                    record_data["lines"]["tovex"].append(line_data)
                    record_data["sub_totals"]["tovex"] += line.product_demand_quantity
                elif 'powder' in category:
                    record_data["lines"]["powder"].append(line_data)
                    record_data["sub_totals"]["powder"] += line.product_demand_quantity
                elif 'accessories' in category:
                    record_data["lines"]["accessories"].append(line_data)
                    record_data["sub_totals"]["accessories"] += line.product_demand_quantity
                elif 'thermotube' in category:
                    record_data["lines"]["thermoube"].append(line_data)
                    record_data["sub_totals"]["thermotube"] += line.product_demand_quantity
                else:
                    record_data["lines"]["other"].append(line_data)
                    record_data["sub_totals"]["other"] += line.product_demand_quantity
                
                sno_counter += 1
                
            record_data["total"] = sum(record_data["sub_totals"].values())
            #record_data["date_from"] = str(self.from_date)
            #record_data["date_to"] = str(self.to_date)
            grand_total += record_data["total"]
            material_data.append(record_data)
        
        # return {"data": material_data, 
        # "grand_total": grand_total,
        # "date_from": self.from_date,
        # "date_to": self.to_date,
        # "date": self.current_date, 
        # "time": self.current_time
        #          }
        return {"data": material_data, 
        "grand_total": grand_total,
        # "date_from": self.from_date,
        # "date_to": self.to_date,
        "date": self.current_date, 
        "time": self.current_time,
        'plans':",".join([plan.name for plan in material_reqs])
                 }



    def generate_report(self):
        # Add logic to generate the Daily production report
        report_data = self.prepare_material_data()
        data =  {} #report_data.get("report")
        return self.env.ref('manufacturing_reports.action_material_requirement_pdf').report_action(
         self, data={'report_data': report_data}
        )


