from odoo import api, fields, models


class UniversityAttendanceThreshold(models.Model):
    _name = 'university.attendance.threshold'
    _description = 'Attendance Threshold'
    _order = 'good_threshold desc'

    name = fields.Char(string='Name', default='Default', required=True)
    good_threshold = fields.Float(string='Good Threshold (%)', default=85.0)
    warning_threshold = fields.Float(string='Warning Threshold (%)', default=75.0)
    critical_threshold = fields.Float(string='Critical Threshold (%)', default=75.0)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def get_default(self):
        record = self.search([], limit=1)
        if not record:
            return self.create({
                'name': 'Default',
                'good_threshold': 85.0,
                'warning_threshold': 75.0,
                'critical_threshold': 75.0,
            })
        return record
