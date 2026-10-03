from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityStudent(models.Model):
    _name = 'university.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Student Name', required=True, tracking=True)
    student_id = fields.Char(string='Student ID', required=True, index=True, tracking=True)
    registration_number = fields.Char(string='Registration Number', required=True, index=True, tracking=True)
    university_id = fields.Char(string='University ID', index=True, copy=False)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    date_of_birth = fields.Date(string='Date of Birth')
    address = fields.Text(string='Address')
    photo = fields.Image(string='Photo')
    department_id = fields.Many2one('university.department', string='Department', required=True)
    program_id = fields.Many2one('university.program', string='Program', required=True)
    section_id = fields.Many2one('university.section', string='Section')
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year')
    semester_id = fields.Many2one('university.semester', string='Semester')
    admission_date = fields.Date(string='Admission Date', default=lambda self: fields.Date.context_today(self))
    academic_status = fields.Selection([
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
        ('on_leave', 'On Leave'),
        ('completed', 'Completed'),
    ], string='Academic Status', default='active', tracking=True)
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')

    attendance_ids = fields.One2many('university.attendance', 'student_id', string='Attendance Records')
    enrollment_ids = fields.One2many('university.course.enrollment', 'student_id', string='Enrollments')
    warning_ids = fields.One2many('university.academic.warning', 'student_id', string='Warnings')
    grade_ids = fields.One2many('university.grade', 'student_id', string='Grades')

    total_sessions = fields.Integer(string='Total Sessions', compute='_compute_attendance_summary', store=True)
    present_sessions = fields.Integer(string='Present', compute='_compute_attendance_summary', store=True)
    absent_sessions = fields.Integer(string='Absent', compute='_compute_attendance_summary', store=True)
    late_sessions = fields.Integer(string='Late', compute='_compute_attendance_summary', store=True)
    excused_sessions = fields.Integer(string='Excused', compute='_compute_attendance_summary', store=True)
    attendance_percentage = fields.Float(string='Attendance Percentage', compute='_compute_attendance_summary', store=True, digits=(16, 2), group_operator='avg')
    risk_level = fields.Selection([
        ('normal', 'Normal'),
        ('attention_required', 'Attention Required'),
        ('at_risk', 'At Risk'),
    ], string='Risk Status', compute='_compute_risk_level', store=True)
    gpa = fields.Float(string='GPA', compute='_compute_gpa', store=True, digits=(16, 2))
    completed_credits = fields.Float(string='Completed Credits', compute='_compute_academic_metrics', store=True)
    failed_courses = fields.Integer(string='Failed Courses', compute='_compute_academic_metrics', store=True)

    _sql_constraints = [
        ('student_id_uniq', 'unique(student_id)', 'Student ID must be unique.'),
        ('registration_number_uniq', 'unique(registration_number)', 'Registration number must be unique.'),
    ]

    @api.constrains('student_id', 'registration_number', 'university_id')
    def _check_unique_values(self):
        for record in self:
            if record.university_id and self.search_count([('university_id', '=', record.university_id), ('id', '!=', record.id)]):
                raise ValidationError('University ID must be unique.')

    @api.depends('attendance_ids.status')
    def _compute_attendance_summary(self):
        for student in self:
            records = student.attendance_ids
            student.total_sessions = len(records)
            student.present_sessions = sum(1 for rec in records if rec.status == 'present')
            student.absent_sessions = sum(1 for rec in records if rec.status == 'absent')
            student.late_sessions = sum(1 for rec in records if rec.status == 'late')
            student.excused_sessions = sum(1 for rec in records if rec.status == 'excused')
            total = len(records)
            if total:
                effective_attended = student.present_sessions + (student.late_sessions * 0.5) + (student.excused_sessions * 0.5)
                student.attendance_percentage = round((effective_attended / total) * 100.0, 2)
            else:
                student.attendance_percentage = 0.0

    @api.depends('attendance_percentage')
    def _compute_risk_level(self):
        threshold = self.env['university.attendance.threshold'].get_default()
        for student in self:
            pct = student.attendance_percentage or 0.0
            if pct >= threshold.good_threshold:
                student.risk_level = 'normal'
            elif pct >= threshold.warning_threshold:
                student.risk_level = 'attention_required'
            else:
                student.risk_level = 'at_risk'

    @api.depends('grade_ids.percentage')
    def _compute_gpa(self):
        for student in self:
            grades = student.grade_ids
            total_points = 0.0
            total_credits = 0.0
            for grade in grades:
                course = grade.course_id
                if course and course.credit_hours:
                    total_points += grade.grade_point * course.credit_hours
                    total_credits += course.credit_hours
            student.gpa = round(total_points / total_credits, 2) if total_credits else 0.0

    @api.depends('grade_ids.score', 'grade_ids.maximum_score', 'grade_ids.percentage')
    def _compute_academic_metrics(self):
        for student in self:
            total_credits = 0.0
            failed = 0
            for grade in student.grade_ids:
                course = grade.course_id
                if course and course.credit_hours:
                    total_credits += course.credit_hours
                if grade.percentage < 50:
                    failed += 1
            student.completed_credits = total_credits
            student.failed_courses = failed

    @api.model
    def _generate_low_attendance_warnings(self):
        threshold = self.env['university.attendance.threshold'].get_default()
        for student in self.search([('active', '=', True)]):
            if student.attendance_percentage < threshold.warning_threshold:
                existing = self.env['university.academic.warning'].search([
                    ('student_id', '=', student.id),
                    ('semester_id', '=', student.semester_id.id or False),
                    ('status', 'in', ['draft', 'issued', 'acknowledged']),
                ], limit=1)
                if existing:
                    continue
                self.env['university.academic.warning'].create({
                    'student_id': student.id,
                    'course_id': False,
                    'semester_id': student.semester_id.id,
                    'academic_year_id': student.academic_year_id.id,
                    'attendance_percentage': student.attendance_percentage,
                    'threshold': threshold.warning_threshold,
                    'warning_level': 'critical' if student.attendance_percentage < threshold.critical_threshold else 'warning',
                    'status': 'issued',
                    'notes': 'Generated automatically for low attendance monitoring.',
                })

    def action_view_attendance(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.attendance',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'target': 'current',
            'name': 'Attendance',
        }

    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.course.enrollment',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'target': 'current',
            'name': 'Enrollments',
        }

    def action_view_warnings(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.academic.warning',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'target': 'current',
            'name': 'Academic Warnings',
        }
