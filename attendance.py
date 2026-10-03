from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityAttendance(models.Model):
    _name = 'university.attendance'
    _description = 'Attendance Record'
    _order = 'date desc, student_id'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    session_id = fields.Many2one('university.attendance.session', string='Attendance Session', required=True)
    course_id = fields.Many2one('university.course', string='Course', compute='_compute_session_data', store=True, readonly=True)
    section_id = fields.Many2one('university.section', string='Section', compute='_compute_session_data', store=True, readonly=True)
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', compute='_compute_session_data', store=True, readonly=True)
    semester_id = fields.Many2one('university.semester', string='Semester', compute='_compute_session_data', store=True, readonly=True)
    department_id = fields.Many2one('university.department', related='student_id.department_id', store=True, readonly=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ], string='Status', default='present', required=True)
    check_in_time = fields.Float(string='Check-in Time')
    check_out_time = fields.Float(string='Check-out Time')
    minutes_late = fields.Integer(string='Minutes Late', default=0)
    notes = fields.Text(string='Notes')
    recorded_by = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user)
    date = fields.Date(string='Date', related='session_id.date', store=True, readonly=True)

    _sql_constraints = [
        ('student_session_unique', 'unique(student_id, session_id)', 'A student cannot be recorded twice in the same attendance session.'),
    ]

    @api.depends('session_id')
    def _compute_session_data(self):
        for record in self:
            if record.session_id:
                record.course_id = record.session_id.course_id
                record.section_id = record.session_id.section_id
                record.academic_year_id = record.session_id.academic_year_id
                record.semester_id = record.session_id.semester_id
            else:
                record.course_id = False
                record.section_id = False
                record.academic_year_id = False
                record.semester_id = False

    @api.onchange('session_id')
    def _onchange_session_id(self):
        if self.session_id:
            self.course_id = self.session_id.course_id
            self.section_id = self.session_id.section_id
            self.academic_year_id = self.session_id.academic_year_id
            self.semester_id = self.session_id.semester_id

    @api.constrains('status')
    def _check_status(self):
        valid = {'present', 'absent', 'late', 'excused'}
        for record in self:
            if record.status not in valid:
                raise ValidationError('Status is invalid.')
