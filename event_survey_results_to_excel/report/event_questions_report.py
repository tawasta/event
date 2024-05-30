##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2024- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################


from odoo import _, models


class SurveyUserInputXlsx(models.AbstractModel):
    _name = "report.survey_user_input_report_xlsx.user_input_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Survey User Input Report XLSX"

    def generate_xlsx_report(self, workbook, data, event_registration_recs):
        sheet = workbook.add_worksheet(_("Event Answers"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)

        row = 0
        col = 0
        col_amount = 0
        answer_lengths = {}

        # Create headers for the columns
        if event_registration_recs:
            sheet_header = (
                "Answers for the event: " + event_registration_recs[0].event_id.name
            )
            sheet.write(row, col, sheet_header, workbook.add_format({"bold": True}))
            row += 1

            col_amount = len(event_registration_recs[0].registration_answer_ids) + 1
            for i in range(col_amount):
                answer_lengths[i] = []

            sheet.write(row, col, "Responder name", workbook.add_format({"bold": True}))
            answer_lengths[col].append(len("Responder name"))
            col += 1

            for question in event_registration_recs[0].registration_answer_ids:
                question_title = question.question_id.title
                sheet.write(
                    row, col, question_title, workbook.add_format({"bold": True})
                )
                answer_lengths[col].append(len(question_title))
                col += 1
            row += 1
            col = 0

        # Put all the answers under the right headers
        for event_reg_rec in event_registration_recs:
            sheet.write(row, col, event_reg_rec.name)
            answer_lengths[col].append(len(event_reg_rec.name))
            col += 1

            for question in event_reg_rec.registration_answer_ids:
                if question.question_type == "text_box":
                    sheet.write(row, col, question.value_text_box)
                    answer_lengths[col].append(len(question.value_text_box))
                    col += 1

                if question.question_type == "simple_choice":
                    sheet.write(row, col, question.value_answer_id.name)
                    answer_lengths[col].append(len(question.value_answer_id.name))
                    col += 1

            row += 1
            col = 0

        # Adjust the width of the columns to fit the longest answer
        for i in range(col_amount):
            sheet.set_column(i, i, max(answer_lengths[i]) + 2)
