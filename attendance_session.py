from odoo import api, fields, models


class UniversityAttendanceSession(models.Model):
    _name = 'university.attendance.session'
    _description = 'Attendance Session'
    _order = 'date desc, start_time desc'

    name = fields.Char(string='Reference', required=True, default='New')
    course_id = fields.Many2one('university.course', string='Course', required=True)
    section_id = fields.Many2one('university.section', string='Section')
    instructor_id = fields.Many2one('res.users', string='Instructor')
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('university.semester', string='Semester', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    room = fields.Char(string='Room')
    topic = fields.Char(string='Topic')
    notes = fields.Text(string='Notes')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    attendance_ids = fields.One2many('university.attendance', 'session_id', string='Attendance Records')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('university.attendance.session') or 'SES00001'
        return super().create(vals)

    def action_open(self):
        self.write({'status': 'open'})

    def action_complete(self):
        self.write({'status': 'completed'})

    def action_cancel(self):
        self.write({'status': 'cancelled'})

    def action_reopen(self):
        self.write({'status': 'open'})
