from odoo import models, fields, api


class QualityInspectionReportWizard(models.TransientModel):
    _name = 'quality.inspection.report.wizard'
    _description = 'Quality Inspection Report Filter Wizard'

    team_id = fields.Many2one('quality.alert.team', string='Team')
    team_all = fields.Boolean(string='All Teams', default=True)

    qir_filter_type = fields.Selection([
        ('single', 'Single QIR'),
        ('range', 'QIR Range')
    ], string='Filter By', default='single')

    qir_id = fields.Many2one('rqi.model', string='QIR (Single)')
    qir_from = fields.Many2one('rqi.model', string='QIR From')
    qir_to = fields.Many2one('rqi.model', string='QIR To')

    product_id = fields.Many2one('product.product', string='Product')
    qir_date_from = fields.Date(string='QIR Date From')
    qir_date_to = fields.Date(string='QIR Date To')
    approval_status = fields.Selection([
        ('approve', 'Approved'),
        ('cancel', 'Rejected'),
        ('all', 'All')
    ], string='Approval Status', default='all')
    lot_id = fields.Many2one('stock.lot', string='Lot')

    # -------------------------
    # Helpers
    # -------------------------
    def _build_domain(self):
        """Prepare domain for searching QIRs"""
        domain = []
        if not self.team_all and self.team_id:
            domain.append(('team_id', '=', self.team_id.id))

        if self.qir_filter_type == 'single' and self.qir_id:
            domain.append(('id', '=', self.qir_id.id))
        elif self.qir_filter_type == 'range' and self.qir_from and self.qir_to:
            domain.append(('id', '>=', self.qir_from.id))
            domain.append(('id', '<=', self.qir_to.id))

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.qir_date_from:
            domain.append(('date', '>=', self.qir_date_from))
        if self.qir_date_to:
            domain.append(('date', '<=', self.qir_date_to))
        if self.approval_status != 'all':
            domain.append(('state_approval', '=', self.approval_status))
        if self.lot_id:
            domain.append(('lot_id', '=', self.lot_id.id))

        return domain

    def prepare_report_data(self):
        """Collect full QIR data (header + lines) for report template"""
        domain = self._build_domain()
        reports = self.env['rqi.model'].search(domain)

        data = []
        for rec in reports:
            # Collect line details
            lines_data = []
            for line in rec.line_id:  # assuming one2many is line_id
                lines_data.append({
                    'code': line.point_id.display_name if line.point_id else '-',
                    'quality_parameter': line.quality_title or '-',
                    'standard': line.x_studio_standard or '-',
                    'norm': line.norm or '-',
                    'norm_unit': line.norm_unit or '-',
                    'tolerance_limit': line.standards or '-',  # if exists
                    'actual_result': line.result or '-',
                    'qic_status': line.state or '-',
                    'remarks': line.remarks or '-',
                    'status_qir': line.status_qir or '-',
                    'action_required': line.fail_type or '-',
                })

            # Collect record-level details
            data.append({
                'name': rec.name,
                'product': rec.product_id.name if rec.product_id else '',
                'supplier': rec.partner_id.name if rec.partner_id else '',
                'doc_reference': rec.doc_refrence or '',
                'doc_date': rec.doc_date or '',
                'lot': rec.lot_id.name if rec.lot_id else '',
                'alt_lot': rec.alt_lot_id.name if rec.alt_lot_id else '',
                'sample': rec.sample or '',
                'team': rec.team_id.name if rec.team_id else '',
                'qir_date': rec.date or '',
                'approved': rec.approved,
                'reject_note': rec.reject_note or '',
                'remarks': rec.reject_note  or '',
                'prepared_by': rec.prepared_by.name if rec.prepared_by else '',
                'approved_by': rec.approved_by.name if rec.approved_by else '',
                'prepared_by_timestamp': rec.prepared_by_timestamp or '',
                'approved_by_timestamp': rec.approved_by_timestamp or '',
                'lines': lines_data,
            })

        return {
            "report": data,
            "filters": {
                "team": self.team_id.name if self.team_id else "All Teams",
                "filter_type": self.qir_filter_type,
                "qir_id": self.qir_id.name if self.qir_id else '',
                "qir_from": self.qir_from.name if self.qir_from else '',
                "qir_to": self.qir_to.name if self.qir_to else '',
                "product": self.product_id.display_name if self.product_id else '',
                "date_from": self.qir_date_from,
                "date_to": self.qir_date_to,
                "approval_status": self.approval_status,
                "lot": self.lot_id.name if self.lot_id else '',
            }
        }


    # -------------------------
    # Report Action
    # -------------------------
    def action_print_pdf_report(self):
        report_data = self.prepare_report_data()
        return self.env.ref(
            'ol_quality_control.action_quality_inspection_report_pdf'
        ).report_action(
            self, data={'report_data': report_data}
        )
