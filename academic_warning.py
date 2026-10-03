from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityAcademicWarning(models.Model):
    _name = 'university.academic.warning'
    _description = 'Academic Warning'
    _order = 'warning_date desc'

    name = fields.Char(string='Reference', required=True, default='New')
    student_id = fields.Many2one('university.student', string='Student', required=True)
    course_id = fields.Many2one('university.course', string='Course')
    semester_id = fields.Many2one('university.semester', string='Semester')
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year')
    attendance_percentage = fields.Float(string='Attendance Percentage', default=0.0)
    threshold = fields.Float(string='Threshold', default=75.0)
    warning_level = fields.Selection([
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Warning Level', default='warning')
    warning_date = fields.Date(string='Warning Date', default=fields.Date.context_today)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('warning_unique', 'unique(student_id, course_id, semester_id, academic_year_id)', 'A similar warning already exists for this student in the same course and academic period.'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('university.academic.warning') or 'WARN00001'
        return super().create(vals)

    @api.constrains('attendance_percentage', 'threshold')
    def _check_thresholds(self):
        for record in self:
            if record.threshold <= 0:
                raise ValidationError('Threshold must be greater than zero.')
            if record.attendance_percentage < 0 or record.attendance_percentage > 100:
                raise ValidationError('Attendance percentage must be between 0 and 100.')
