import base64
import csv
import io

from odoo import fields, models


class UniversityAttendanceImportWizard(models.TransientModel):
    _name = 'university.attendance.import.wizard'
    _description = 'Attendance Import Wizard'

    data_file = fields.Binary(string='CSV File', required=True)
    filename = fields.Char(string='Filename')
    import_result = fields.Text(string='Import Result', readonly=True)

    def _find_student(self, row):
        student_id = (row.get('Student ID') or '').strip()
        registration_number = (row.get('Registration Number') or '').strip()
        university_id = (row.get('University ID') or '').strip()
        domain = []
        if student_id:
            domain = [('student_id', '=', student_id)]
        elif registration_number:
            domain = [('registration_number', '=', registration_number)]
        elif university_id:
            domain = [('university_id', '=', university_id)]
        if not domain:
            return False
        return self.env['university.student'].search(domain, limit=1)

    def action_import(self):
        if not self.data_file:
            return {'type': 'ir.actions.act_window_close'}

        decoded = base64.b64decode(self.data_file)
        text = decoded.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))

        imported = 0
        skipped = 0
        failed = 0
        errors = []

        for row in reader:
            student = self._find_student(row)
            if not student:
                failed += 1
                errors.append(f"Missing student: {row}")
                continue

            course_code = (row.get('Course Code') or '').strip()
            course = self.env['university.course'].search([('code', '=', course_code)], limit=1)
            if not course:
                failed += 1
                errors.append(f"Missing course: {course_code}")
                continue

            date_value = (row.get('Date') or '').strip()
            if not date_value:
                failed += 1
                errors.append(f"Missing date for student {student.student_id}")
                continue

            status = (row.get('Status') or '').strip().lower()
            if status not in {'present', 'absent', 'late', 'excused'}:
                failed += 1
                errors.append(f"Invalid status for student {student.student_id}: {status}")
                continue

            session = self.env['university.attendance.session'].search([
                ('course_id', '=', course.id),
                ('date', '=', date_value),
                ('section_id', '=', student.section_id.id if student.section_id else False),
            ], limit=1)

            if not session:
                session = self.env['university.attendance.session'].create({
                    'name': self.env['ir.sequence'].next_by_code('university.attendance.session') or 'SES00001',
                    'course_id': course.id,
                    'section_id': student.section_id.id if student.section_id else False,
                    'academic_year_id': student.academic_year_id.id if student.academic_year_id else False,
                    'semester_id': student.semester_id.id if student.semester_id else False,
                    'date': date_value,
                    'status': 'open',
                    'instructor_id': self.env.user.id,
                })

            if self.env['university.attendance'].search_count([
                ('student_id', '=', student.id),
                ('session_id', '=', session.id),
            ]):
                skipped += 1
                continue

            self.env['university.attendance'].create({
                'student_id': student.id,
                'session_id': session.id,
                'status': status,
                'recorded_by': self.env.user.id,
                'notes': row.get('Notes') or '',
            })
            imported += 1

        self.import_result = (
            f"Imported: {imported}\n"
            f"Skipped: {skipped}\n"
            f"Failed: {failed}\n"
            + (f"Errors:\n{chr(10).join(errors[:10])}" if errors else '')
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'name': 'Import Result',
        }
