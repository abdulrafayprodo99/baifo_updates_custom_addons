from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, formatLang, end_of,float_round
from dateutil.relativedelta import relativedelta
# from odoo.tools.float_utils import float_round
import datetime
import logging
import calendar

_logger = logging.getLogger(__name__)


# Get the current year and month
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month

# Get the number of days in the current month
_, days_per_month = calendar.monthrange(current_year, current_month)




DAYS_PER_MONTH = 30
DAYS_PER_YEAR = DAYS_PER_MONTH * 12
class AccountAsset(models.Model):
    _inherit = 'account.asset'

    old_asset_original_value = fields.Float(string="Old Assets Original Value")
    sr_no = fields.Integer(string="Sr No")
    asset_class = fields.Char(string='Asset Class')
    sub_asset_class = fields.Char(string='Sub Asset Class')
    
    
    def get_days_in_selected_month(self):
        if self.date:
            # Extract the year and month from the date_field
            date_value = fields.Datetime.from_string(self.date)
            selected_year = date_value.year
            selected_month = date_value.month
            
            # Get the number of days in the selected month
            _, days_in_month = calendar.monthrange(selected_year, selected_month)
            
            return days_in_month
        return 30


    @api.depends('method_number', 'method_period', 'prorata_computation_type')
    def _compute_lifetime_days(self):
        for asset in self:
            if asset.prorata_computation_type == 'daily_computation':
                asset.asset_lifetime_days = (asset.prorata_date + relativedelta(months=int(asset.method_period) * asset.method_number) - asset.prorata_date).days
            else:
                asset.asset_lifetime_days = int(asset.method_period) * asset.method_number * DAYS_PER_MONTH

    
    @api.depends('prorata_date', 'prorata_computation_type', 'asset_paused_days')
    def _compute_paused_prorata_date(self):
        for asset in self:
            if not asset.prorata_date:
                raise UserError(_('Prorata Date can not be empty'))
            if asset.prorata_computation_type == 'daily_computation':
                asset.paused_prorata_date = asset.prorata_date + relativedelta(days=asset.asset_paused_days)
            else:
                asset.paused_prorata_date = asset.prorata_date + relativedelta(
                    months=int(asset.asset_paused_days / DAYS_PER_MONTH),
                    days=asset.asset_paused_days % DAYS_PER_MONTH
                )

    
    def _get_delta_days(self, start_date, end_date):
        """Compute how many days there are between 2 dates.

        The computation is different if the asset is in daily_computation or not.
        """
        self.ensure_one()
        if self.prorata_computation_type == 'daily_computation':
            # Compute how many days there are between 2 dates using a daily_computation method
            return (end_date - start_date).days + 1
        else:
            # Compute how many days there are between 2 dates counting 30 days per month
            # Get how many days there are in the start date month
            start_date_days_month = end_of(start_date, 'month').day
            # Get how many days there are in the start date month (e.g: June 20th: (30 * (30 - 20 + 1)) / 30 = 11)
            start_prorata = (start_date_days_month - start_date.day + 1) / start_date_days_month
            # Get how many days there are in the end date month (e.g: You're the August 14th: (14 * 30) / 31 = 13.548387096774194)
            end_prorata = end_date.day / end_of(end_date, 'month').day
            # Compute how many days there are between these 2 dates
            # e.g: 13.548387096774194 + 11 + 360 * (2020 - 2020) + 30 * (8 - 6 - 1) = 24.548387096774194 + 360 * 0 + 30 * 1 = 54.548387096774194 day
            return sum((
                start_prorata * DAYS_PER_MONTH,
                end_prorata * DAYS_PER_MONTH,
                (end_date.year - start_date.year) * DAYS_PER_YEAR,
                (end_date.month - start_date.month - 1) * DAYS_PER_MONTH
            ))

    def _recompute_board(self, start_depreciation_date=False):
        self.ensure_one()
        # All depreciation moves that are posted
        posted_depreciation_move_ids = self.depreciation_move_ids.filtered(
            lambda mv: mv.state == 'posted' and not mv.asset_value_change
        ).sorted(key=lambda mv: (mv.date, mv.id))

        imported_amount = self.already_depreciated_amount_import
        residual_amount = self.value_residual
        if not posted_depreciation_move_ids:
            residual_amount += imported_amount
        residual_declining = residual_amount

        # Days already depreciated
        days_already_depreciated = sum(posted_depreciation_move_ids.mapped('asset_number_days'))
        days_left_to_depreciated = self.asset_lifetime_days - days_already_depreciated
        days_already_added = sum([(mv.date - mv.asset_depreciation_beginning_date).days + 1 for mv in posted_depreciation_move_ids])
        start_depreciation_date = self.paused_prorata_date + relativedelta(days=days_already_added)
        final_depreciation_date = self.paused_prorata_date + relativedelta(months=int(self.method_period) * self.method_number, days=-1)
        final_depreciation_date = self._get_end_period_date(final_depreciation_date)
        depreciation_move_values = []
        if not float_is_zero(self.value_residual, precision_rounding=self.currency_id.rounding):
            while days_already_depreciated < self.asset_lifetime_days:
                period_end_depreciation_date = self._get_end_period_date(start_depreciation_date)
                period_end_fiscalyear_date = self.company_id.compute_fiscalyear_dates(period_end_depreciation_date).get('date_to')
                days, amount = self._compute_board_amount(residual_amount, start_depreciation_date, period_end_depreciation_date, days_already_depreciated, days_left_to_depreciated, residual_declining)
                residual_amount -= amount
                if not posted_depreciation_move_ids:
                    # self.already_depreciated_amount_import management.
                    # Subtracts the imported amount from the first depreciation moves until we reach it
                    # (might skip several depreciation entries)
                    if abs(imported_amount) <= abs(amount):
                        amount -= imported_amount
                        imported_amount = 0
                    else:
                        imported_amount -= amount
                        amount = 0

                if self.method == 'degressive_then_linear' and final_depreciation_date < period_end_depreciation_date:
                    period_end_depreciation_date = final_depreciation_date
                if not float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    # For deferred revenues, we should invert the amounts.
                    if self.asset_type == 'sale':
                        amount *= -1
                    depreciation_move_values.append(self.env['account.move']._prepare_move_for_asset_depreciation({
                        'amount': amount,
                        'asset_id': self,
                        'depreciation_beginning_date': start_depreciation_date,
                        'date': period_end_depreciation_date,
                        'asset_number_days': days,
                    }))
                days_already_depreciated += days

                if period_end_depreciation_date == period_end_fiscalyear_date:
                    days_left_to_depreciated = self.asset_lifetime_days - days_already_depreciated
                    residual_declining = residual_amount

                start_depreciation_date = period_end_depreciation_date + relativedelta(days=1)

        return depreciation_move_values

    def get_days_in_year(self,date):
        if date:
            # Convert the date field to a Python date object
            date_value = fields.Date.from_string(date)
            # Extract the year and month from the date
            year = date_value.year
            month = date_value.month
            
            # Determine the start and end year of the fiscal period
            if month >= 7:  # If the month is July or later, fiscal year starts in the current year
                start_year = year
                end_year = year + 1
            else:  # If the month is before July, fiscal year started last year
                start_year = year - 1
                end_year = year
            
            # Check if any of the fiscal year includes a leap year
            # Fiscal year spans July of start_year to June of end_year
            if calendar.isleap(end_year):  # Only the second year matters because it includes February
                return 366  # Leap year within the fiscal period
            else:
                return 365  # No leap year within the fiscal period
        return 365 
    
    def _compute_board_amount(self, residual_amount, period_start_date, period_end_date, days_already_depreciated, days_left_to_depreciated, residual_declining):
        if self.asset_lifetime_days == 0:
            return 0, 0
        number_days = self._get_delta_days(period_start_date, period_end_date)
        total_days = number_days + days_already_depreciated
        DAYS_PER_YEAR = self.get_days_in_year(period_start_date)
        if self.method in ('degressive', 'degressive_then_linear'):
            # Declining by year but divided per month
            # We compute the amount of the period based on ratio how many days there are in the period
            # e.g: monthly period = 30 days --> (30/360) * 12000 * 0.4
            # => For each month in the year we will decline the same amount.
            amount = (number_days / DAYS_PER_YEAR) * residual_declining * self.method_progress_factor
        else:
            computed_linear_amount = (self.total_depreciable_value * total_days / self.asset_lifetime_days) + residual_amount - self.total_depreciable_value
            if float_compare(residual_amount, 0, precision_rounding=self.currency_id.rounding) >= 0:
                linear_amount = min(computed_linear_amount, residual_amount)
                amount = max(linear_amount, 0)
            else:
                linear_amount = max(computed_linear_amount, residual_amount)
                amount = min(linear_amount, 0)
        if self.method == 'degressive_then_linear' and days_left_to_depreciated != 0:
            linear_amount = number_days * self.total_depreciable_value / self.asset_lifetime_days
            amount = max(linear_amount, amount, key=abs)

        # if self.method == 'degressif_chelou' and days_left_to_depreciated != 0:
        #     linear_amount = number_days * residual_declining / days_left_to_depreciated
        #     if float_compare(residual_amount, 0, precision_rounding=self.currency_id.rounding) >= 0:
        #         amount = max(linear_amount, amount)
        #     else:
        #         amount = min(linear_amount, amount)


        if self.method != 'degressive' and (abs(residual_amount) < abs(amount) or total_days >= self.asset_lifetime_days):
            
            # If the residual amount is less than the computed amount, we keep the residual amount
            # If total_days is greater or equals to asset lifetime days, it should mean that
            # the asset will finish in this period and the value for this period is equals to the residual amount.
            amount = residual_amount
        return number_days, self.currency_id.round(amount)
