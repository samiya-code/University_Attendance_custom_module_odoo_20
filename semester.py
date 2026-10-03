from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversitySemester(models.Model):
    _name = 'university.semester'
    _description = 'Semester'
    _order = 'start_date desc'

    name = fields.Char(string='Semester Name', required=True)
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    semester_type = fields.Selection([
        ('semester_1', 'Semester 1'),
        ('semester_2', 'Semester 2'),
        ('summer', 'Summer'),
    ], string='Semester Type', default='semester_1', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date <= record.start_date:
                raise ValidationError('Semester end date must be after the start date.')
