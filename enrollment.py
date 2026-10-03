from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityCourseEnrollment(models.Model):
    _name = 'university.course.enrollment'
    _description = 'Course Enrollment'
    _order = 'enrollment_date desc'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    course_id = fields.Many2one('university.course', string='Course', required=True)
    section_id = fields.Many2one('university.section', string='Section')
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('university.semester', string='Semester', required=True)
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.context_today)
    status = fields.Selection([
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    ], string='Status', default='enrolled', required=True)

    _sql_constraints = [
        ('student_course_year_sem_unique', 'unique(student_id, course_id, academic_year_id, semester_id)', 'Duplicate enrollment is not allowed for the same student, course, academic year, and semester.'),
    ]

    @api.constrains('student_id', 'course_id')
    def _check_student_course(self):
        for record in self:
            if not record.student_id or not record.course_id:
                raise ValidationError('Student and course are required.')
