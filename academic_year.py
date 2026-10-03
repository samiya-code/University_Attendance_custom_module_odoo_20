from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityAcademicYear(models.Model):
    _name = 'university.academic.year'
    _description = 'Academic Year'
    _order = 'start_date desc'

    name = fields.Char(string='Academic Year', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    active = fields.Boolean(string='Active', default=True)

    semester_ids = fields.One2many('university.semester', 'academic_year_id', string='Semesters')
    section_ids = fields.One2many('university.section', 'academic_year_id', string='Sections')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date <= record.start_date:
                raise ValidationError('End date must be after the start date.')
