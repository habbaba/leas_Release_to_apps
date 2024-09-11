# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from datetime import datetime, timedelta, time
from odoo.exceptions import UserError
from odoo.modules import module
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
                raise UserError(_("Not allowed to be greater than the started quantity."))

    @api.constrains('qty_started')
    def _check_qty_started(self):
        for line in self:
            if line.qty_started > line.workorder_id.qty_production:
                raise UserError(_("Cannot Exceed WorkOrder Quantity."))
            last_rec = line.next_rec
            while last_rec and last_rec.next_rec:
                last_rec = last_rec.next_rec
            qty_comp = last_rec.qty_completed or line.qty_completed
            if line.qty_started < qty_comp:
                raise UserError(_("Not allowed to be less than the completed quantity."))

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

        # Same logic for efficiency calculation

    def unlink(self):
        if self.env.context.get('_force_unlink'):
            return super().unlink()
        for line in self:
            rec = self.sudo().search([('next_rec', '=', line.id)], limit=1)
            if line.action_type == 'finish' or line.next_rec:
                raise UserError(_("Records cannot be deleted. You can achieve the same "
                                  "result by modifying the timestamp or completing the quantity."))
            elif rec:
                rec.next_rec = False
            else:
                self.env['mrp.workorder'].sudo().browse(line.workorder_id.id).qty_operation_wip = \
                    line.workorder_id.qty_operation_wip - line.qty_started
            line.sudo().with_context(_force_unlink=True).unlink()

    @staticmethod
    def num_to_time(num):
        hours_from = int(num)
        minutes_from = int((hours_from - num) * 60)
        return time(hours_from, minutes_from, 0)

    @api.depends('workorder_id.qty_production', 'next_rec.qty_completed')
    def _compute_thirty_daily_efficiency(self):
        """
        Compute method for `thirty_daily_efficiency` that calculates efficiency
        over the past 30 days or based on completed and production quantities.
        """
        for record in self:
            try:
                if not record.workorder_id or not record.workorder_id.qty_production:
                    record.thirty_daily_efficiency = 0.0
                    continue

                total_efficiency = 0.0
                total_qty = 0.0

                # Fetch workorders and compute efficiency
                if record.qty_completed and record.qty_started:
                    efficiency = (record.qty_completed / record.qty_started) * 100
                    total_efficiency += efficiency
                    total_qty += 1

                # Compute the final efficiency based on total_qty
                if total_qty > 0:
                    record.thirty_daily_efficiency = total_efficiency / total_qty
                else:
                    record.thirty_daily_efficiency = 0.0

            except Exception as e:
                _logger.error(f"Error computing thirty_daily_efficiency for Record {record.id}: {e}")
                record.thirty_daily_efficiency = 0.0
