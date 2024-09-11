# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from datetime import datetime, timedelta, time
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MrpWorkcenterproductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    qty_started = fields.Float('Started Quantity')
    qty_completed = fields.Float('Completed Quantity')
    action_type = fields.Selection([('pause', 'Pause'), ('block', 'Block'), ('finish', 'Finish')])
    next_rec = fields.Many2one('mrp.workcenter.productivity', 'Next Record')
    workorder_state = fields.Selection(string='WorkOrder Status', related='workorder_id.state')
    
    thirty_daily_efficiency = fields.Float(compute='_compute_thirty_daily_efficiency', store=True)

    @api.depends('workorder_id', 'workorder_id.qty_production', 'workorder_id.qty_completed')
    def _compute_thirty_daily_efficiency(self):
        """
        Compute method for thirty_daily_efficiency which calculates efficiency
        over the past 30 days.
        """
        for line in self:
            try:
                workorder = line.workorder_id
                if not workorder or not workorder.qty_production or not workorder.qty_completed:
                    line.thirty_daily_efficiency = 0.0
                    continue
                
                # Ensure we have valid values to avoid division errors
                total_efficiency = 0.0
                qty_production = workorder.qty_production
                qty_completed = workorder.qty_completed

                if qty_production > 0:
                    total_efficiency = (qty_completed / qty_production) * 100
                else:
                    total_efficiency = 0.0
                
                line.thirty_daily_efficiency = total_efficiency

            except Exception as e:
                # Log error in case something goes wrong
                _logger.error(f"Error computing thirty_daily_efficiency for Workorder {line.id}: {e}")
                line.thirty_daily_efficiency = 0.0

    @api.onchange('qty_started')
    def _onchange_qty_started(self):
        if self.env.context.get('_prevent_onchange') or not self.id.origin:
            return
        for line in self:
            old_value = line._origin.qty_started if line._origin else False
            new_value = line.qty_started
            diff = new_value - old_value
            same_rec = last_rec = line.next_rec
            while last_rec and last_rec.next_rec:
                last_rec = last_rec.next_rec
                same_rec |= last_rec
            is_comp = last_rec.qty_completed > 0 or line.qty_completed > 0 or \
                      last_rec.action_type == 'finish' or line.action_type == 'finish'

            # upward
            rec = self.sudo().search([('next_rec', '=', line.id.origin)], limit=1)
            while rec and rec.next_rec:
                same_rec |= rec
                rec = self.env['mrp.workcenter.productivity'].sudo().search([('next_rec', '=', rec.id)], limit=1)
            # update WorkCenter_productivity
            prod_val = {'qty_started': new_value}
            same_rec.sudo().with_context(_prevent_onchange=True).write(prod_val)
            # Update WorkOrder
            if not is_comp:
                wo_val = {
                    'qty_operation_wip': line.workorder_id.qty_operation_wip + diff
                }
                self.env['mrp.workorder'].sudo().search([('id', '=', line.workorder_id.id.origin)]).write(wo_val)

    @api.onchange('qty_completed')
    def _onchange_qty_completed(self):
        for line in self:
            old_value = line._origin.qty_completed if line._origin else False
            new_value = line.qty_completed
            diff = new_value - old_value
            val = {
                'qty_operation_comp': line.workorder_id.qty_operation_comp + diff
            }
            self.env['mrp.workorder'].sudo().search([('id', '=', line.workorder_id.id.origin)]).write(val)
            if line.workorder_id.qty_operation_comp + diff == line.workorder_id.qty_production:
                wo = self.env['mrp.workorder'].sudo().browse(line.workorder_id.id.origin)
                wo.button_finish()

    @api.constrains('qty_completed')
    def _check_qty_completed(self):
        for line in self:
            if line.qty_completed > line.qty_started:
                raise UserError(_(u"Not allowed to be greater than the started quantity."))

    @api.constrains('qty_started')
    def _check_qty_started(self):
        for line in self:
            if line.qty_started > line.workorder_id.qty_production:
                raise UserError(_(u"Cannot Exceed WorkOrder Quantity."))
            last_rec = line.next_rec
            while last_rec and last_rec.next_rec:
                last_rec = last_rec.next_rec
            qty_comp = last_rec.qty_completed or line.qty_completed
            if line.qty_started < qty_comp:
                raise UserError(_(u"Not allowed to be less than the completed quantity."))

    def get_processing_time_recs(self):
        self.ensure_one()
        time_recs = self.sudo().browse(self.id)
        rec = self.sudo().search([('next_rec', '=', self.id)], limit=1)
        time_recs |= rec
        while rec and rec.next_rec:
            time_recs |= rec
            rec = self.sudo().search([('next_rec', '=', rec.id)], limit=1)
        return time_recs

    def get_dates_by_log(self, time_log=None):
        if time_log is None:
            time_log = self
        start_datetime = min(time_log.mapped('date_start'))
        try:
            end_datetime = max(time_log.mapped('date_end'))
        except:
            end_datetime = datetime.combine(start_datetime + timedelta(days=1), time(0, 0, 0))
        dates = []
        current_date = start_datetime

        while current_date <= end_datetime:
            dates.append(datetime.combine(current_date.date(), time(0, 0, 0)))
            current_date += timedelta(days=1)

        return dates

    def calc_dates_efficiency(self):
        time_log = self
        temp_daily_efficiency = []
        for log in time_log:
            if log.action_type == 'finish':
                temp_daily_efficiency += log.calc_daily_efficiency()

        date_to_duration = {}
        for item in temp_daily_efficiency:
            date = item['date']
            if date in date_to_duration:
                date_to_duration[date] += item['duration']
            else:
                date_to_duration[date] = item['duration']
        daily_efficiency = {}
        for temp in temp_daily_efficiency:
            date = temp['date']
            duration = temp['duration']
            efficiency = temp['efficiency']
            total_duration = date_to_duration[date]
            if date in daily_efficiency:
                daily_efficiency[date]['efficiency'] += efficiency * (duration / total_duration)
                daily_efficiency[date]['duration'] += duration
            else:
                daily_efficiency[date] = {'duration': duration,
                                          'efficiency': efficiency * (duration / total_duration)}

        sorted_list = sorted(daily_efficiency.items(), key=lambda item: item[0])

        return [{'date': date.strftime("%Y-%m-%d"),
                 'duration': round(info['duration'], 2),
                 'efficiency': round(info['efficiency'], 2)} for date, info in sorted_list]

    def calc_daily_efficiency(self):
        self.ensure_one()
        production_efficiencies = []
        daily_avg_efficiencies = []
        output_quantity = self.qty_completed
        processing_times = self.get_processing_time_recs()
        if self.workorder_id:
            theoretical_time_per_product = self.workorder_id.duration_expected / self.workorder_id.qty_production
        else:
            return production_efficiencies

        attendance_obj = self.env['resource.calendar.attendance'].sudo()
        resource_calendar = self.sudo().workcenter_id.resource_calendar_id
        daily_duration = []
        for pro_time in processing_times:
            start_datetime = pro_time.date_start
            end_datetime = pro_time.date_end
            if not end_datetime:
                end_datetime = datetime.combine(start_datetime + timedelta(days=1), time(0, 0, 0))
            current_datetime = start_datetime
            total_production_time = timedelta(minutes=0)
            daily_production_time = timedelta(minutes=0)

            week_type = -1
            if resource_calendar.two_weeks_calendar:
                week_type = attendance_obj.get_week_type(start_datetime)
            scheduling_plan = resource_calendar.attendance_ids.sorted(lambda t: t.hour_from)

            while current_datetime < end_datetime:
                match_time = timedelta(minutes=1)
                current_dayofweek = current_datetime.weekday()
                current_plan = [plan for plan in scheduling_plan if
                                plan.dayofweek == str(current_dayofweek) and plan.hour_from != plan.hour_to != 0 and (
                                        week_type == -1 or plan.week_type == week_type)]
                for plan in current_plan:
                    scheduled_end = datetime.combine(current_datetime.date(), self.num_to_time(plan.hour_to))
                    scheduled_start = datetime.combine(current_datetime.date(), self.num_to_time(plan.hour_from))
                    if scheduled_end > current_datetime >= scheduled_start:
                        end_time_to_use = min(scheduled_end, end_datetime)
