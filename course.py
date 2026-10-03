from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityCourse(models.Model):
    _name = 'university.course'
    _description = 'Course'
    _order = 'name'

    name = fields.Char(string='Course Name', required=True)
    code = fields.Char(string='Course Code', required=True)
    credit_hours = fields.Float(string='Credit Hours', default=3.0)
    department_id = fields.Many2one('university.department', string='Department', required=True)
    program_id = fields.Many2one('university.program', string='Program', required=True)
    course_type = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('elective', 'Elective'),
        ('practical', 'Practical'),
        ('laboratory', 'Laboratory'),
    ], string='Course Type', default='mandatory', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    enrollment_ids = fields.One2many('university.course.enrollment', 'course_id', string='Enrollments')
    attendance_session_ids = fields.One2many('university.attendance.session', 'course_id', string='Sessions')

    _sql_constraints = [
        ('course_code_uniq', 'unique(code)', 'Course code must be unique.'),
    ]

    @api.constrains('credit_hours')
    def _check_credit_hours(self):
        for record in self:
            if record.credit_hours <= 0:
                raise ValidationError('Credit hours must be greater than zero.')
