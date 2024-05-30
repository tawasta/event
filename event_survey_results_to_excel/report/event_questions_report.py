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
from odoo.exceptions import UserError


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

        # title_index_dict is a dict to keep track on what column the
        # answer should be placed.
        # The answers can be in different order on each event.registration rec,
        # so the answers can't just be placed from left to right.
        title_index_dict = {}

        # Create headers for the columns
        if event_registration_recs:
            prev_event_name = event_registration_recs[0].event_id.name
            for event_reg in event_registration_recs:
                if event_reg.event_id.name != prev_event_name:
                    raise UserError(
                        _(
                            "You are only able to export the answers of a"
                            " single event into XLSX file. Please select"
                            " an event and the attendee list of that event"
                            "to export the answers."
                        )
                    )
                prev_event_name = event_reg.event_id.name
            sheet_header = (
                "Answers for the event: " + event_registration_recs[0].event_id.name
            )
            sheet.write(row, col, sheet_header, workbook.add_format({"bold": True}))
            row += 1

            col_amount = len(event_registration_recs[0].event_id.question_ids) + 1
            for i in range(col_amount):
                answer_lengths[i] = []

            sheet.write(row, col, "Responder name", workbook.add_format({"bold": True}))
            answer_lengths[col].append(len("Responder name"))
            title_index_dict["Responder name"] = 0
            col += 1

            for question in event_registration_recs[0].event_id.question_ids:
                question_title = question.title
                sheet.write(
                    row, col, question_title, workbook.add_format({"bold": True})
                )
                title_index_dict[str(question_title)] = col
                answer_lengths[col].append(len(question_title))
                col += 1
            row += 1
            col = 0

        # Put all the answers under the right headers
        if event_registration_recs:

            for event_reg_rec in event_registration_recs:
                sheet.write(row, title_index_dict["Responder name"], event_reg_rec.name)
                answer_lengths[title_index_dict["Responder name"]].append(
                    len(event_reg_rec.name)
                )

                for question in event_reg_rec.registration_answer_ids:

                    question_title = str(question.question_id.title)
                    if question.question_type == "text_box":
                        sheet.write(
                            row,
                            title_index_dict[question_title],
                            question.value_text_box,
                        )
                        answer_lengths[title_index_dict[question_title]].append(
                            len(question.value_text_box)
                        )

                    if question.question_type == "simple_choice":
                        sheet.write(
                            row,
                            title_index_dict[question_title],
                            question.value_answer_id.name,
                        )
                        answer_lengths[title_index_dict[question_title]].append(
                            len(question.value_answer_id.name)
                        )

                row += 1

            # Adjust the width of the columns to fit the longest answer
            for i in range(col_amount):
                sheet.set_column(i, i, max(answer_lengths[i]) + 2)
