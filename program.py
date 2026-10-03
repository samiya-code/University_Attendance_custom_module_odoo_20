from odoo import fields, models


class UniversityProgram(models.Model):
    _name = 'university.program'
    _description = 'Program'
    _order = 'name'

    name = fields.Char(string='Program Name', required=True)
    code = fields.Char(string='Program Code', required=True)
    department_id = fields.Many2one('university.department', string='Department', required=True)
    degree_type = fields.Selection([
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ], string='Degree Type', default='bachelor', required=True)
    duration = fields.Integer(string='Duration (Years)', default=4)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    section_ids = fields.One2many('university.section', 'program_id', string='Sections')
    course_ids = fields.One2many('university.course', 'program_id', string='Courses')

    _sql_constraints = [
        ('program_code_uniq', 'unique(code)', 'Program code must be unique.'),
    ]
