from odoo import fields, models


class UniversityDepartment(models.Model):
    _name = 'university.department'
    _description = 'Department'
    _order = 'name'

    name = fields.Char(string='Department Name', required=True)
    code = fields.Char(string='Department Code', required=True)
    head_id = fields.Many2one('res.users', string='Department Head')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    student_ids = fields.One2many('university.student', 'department_id', string='Students')
    program_ids = fields.One2many('university.program', 'department_id', string='Programs')
    course_ids = fields.One2many('university.course', 'department_id', string='Courses')

    _sql_constraints = [
        ('department_code_uniq', 'unique(code)', 'Department code must be unique.'),
    ]
