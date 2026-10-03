from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityGradeScale(models.Model):
    _name = 'university.grade.scale'
    _description = 'Grade Scale'
    _order = 'minimum_score desc'

    name = fields.Char(string='Grade', required=True)
    minimum_score = fields.Float(string='Minimum Score', required=True)
    maximum_score = fields.Float(string='Maximum Score', required=True)
    letter_grade = fields.Char(string='Letter Grade', required=True)
    grade_point = fields.Float(string='Grade Point', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def get_grade_for_score(self, score):
        if score is None:
            return False
        return self.search([
            ('minimum_score', '<=', score),
            ('maximum_score', '>=', score),
        ], limit=1)


class UniversityGrade(models.Model):
    _name = 'university.grade'
    _description = 'Academic Grade'
    _order = 'student_id, course_id'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    course_id = fields.Many2one('university.course', string='Course', required=True)
    semester_id = fields.Many2one('university.semester', string='Semester', required=True)
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    assessment_type = fields.Selection([
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm'),
        ('final_exam', 'Final Exam'),
        ('project', 'Project'),
        ('practical', 'Practical'),
        ('other', 'Other'),
    ], string='Assessment Type', default='final_exam', required=True)
    score = fields.Float(string='Score', default=0.0)
    maximum_score = fields.Float(string='Maximum Score', default=100.0)
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    letter_grade = fields.Char(string='Letter Grade', compute='_compute_grade', store=True)
    grade_point = fields.Float(string='Grade Point', compute='_compute_grade', store=True)
    remarks = fields.Text(string='Remarks')

    @api.depends('score', 'maximum_score')
    def _compute_percentage(self):
        for record in self:
            if record.maximum_score > 0:
                record.percentage = round((record.score / record.maximum_score) * 100.0, 2)
            else:
                record.percentage = 0.0

    @api.depends('percentage')
    def _compute_grade(self):
        scale_model = self.env['university.grade.scale']
        for record in self:
            grading = scale_model.get_grade_for_score(record.percentage)
            if grading:
                record.letter_grade = grading.letter_grade
                record.grade_point = grading.grade_point
            else:
                record.letter_grade = 'F'
                record.grade_point = 0.0

    @api.constrains('score', 'maximum_score')
    def _check_score(self):
        for record in self:
            if record.score < 0:
                raise ValidationError('Score cannot be negative.')
            if record.maximum_score <= 0:
                raise ValidationError('Maximum score must be greater than zero.')
            if record.score > record.maximum_score:
                raise ValidationError('Score cannot exceed the maximum score.')
