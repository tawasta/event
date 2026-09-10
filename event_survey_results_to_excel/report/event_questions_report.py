from odoo import _, models
from odoo.exceptions import UserError


class EventRegistrationAnswersXlsx(models.AbstractModel):
    _name = "report.event_survey_results_to_excel.answers_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Event Registration Answers XLSX"

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
        # The answers can be in different order on each event.registration
        # rec, so the answers can't just be placed from left to right.
        title_index_dict = {}

        if not event_registration_recs:
            return

        event = event_registration_recs[0].event_id
        if any(
            registration.event_id != event for registration in event_registration_recs
        ):
            raise UserError(
                _(
                    "You are only able to export the answers of a single"
                    " event into XLSX file. Please select an event and the"
                    " attendee list of that event to export the answers."
                )
            )

        bold = workbook.add_format({"bold": True})

        sheet.write(row, col, _("Answers for the event: %s", event.name), bold)
        row += 1

        col_amount = len(event.question_ids) + 1
        for i in range(col_amount):
            answer_lengths[i] = []

        sheet.write(row, col, _("Responder name"), bold)
        answer_lengths[col].append(len(_("Responder name")))
        title_index_dict[_("Responder name")] = 0
        col += 1

        for question in event.question_ids:
            sheet.write(row, col, question.title, bold)
            title_index_dict[question.title] = col
            answer_lengths[col].append(len(question.title))
            col += 1
        row += 1
        col = 0

        for event_reg_rec in event_registration_recs:
            responder_col = title_index_dict[_("Responder name")]
            sheet.write(row, responder_col, event_reg_rec.name)
            answer_lengths[responder_col].append(len(event_reg_rec.name))

            for answer in event_reg_rec.registration_answer_ids:
                question_col = title_index_dict.get(answer.question_id.title)
                if question_col is None:
                    continue

                if answer.question_type == "simple_choice":
                    value = answer.value_answer_id.name or ""
                else:
                    value = answer.value_text_box or ""

                sheet.write(row, question_col, value)
                answer_lengths[question_col].append(len(value))

            row += 1

        for i in range(col_amount):
            if answer_lengths[i]:
                sheet.set_column(i, i, max(answer_lengths[i]) + 2)
