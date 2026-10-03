from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversitySection(models.Model):
    _name = 'university.section'
    _description = 'Section'
    _order = 'name'

    name = fields.Char(string='Section Name', required=True)
    code = fields.Char(string='Section Code', required=True)
    program_id = fields.Many2one('university.program', string='Program', required=True)
    department_id = fields.Many2one('university.department', string='Department', required=True)
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('university.semester', string='Semester', required=True)
    advisor_id = fields.Many2one('res.users', string='Academic Advisor')
    maximum_students = fields.Integer(string='Maximum Students', default=40)
    active = fields.Boolean(string='Active', default=True)

    student_ids = fields.One2many('university.student', 'section_id', string='Students')
    attendance_session_ids = fields.One2many('university.attendance.session', 'section_id', string='Sessions')

    _sql_constraints = [
        ('section_code_uniq', 'unique(code)', 'Section code must be unique.'),
    ]

    @api.constrains('maximum_students')
    def _check_maximum_students(self):
        for record in self:
            if record.maximum_students <= 0:
                raise ValidationError('Maximum students must be greater than zero.')
