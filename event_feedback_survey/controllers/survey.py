##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
# 1. Standard library imports:
import logging

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.survey.controllers.main import Survey

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class SurveyFeedbackEvent(Survey):

    # flake8: noqa: C901
    @http.route(
        '/survey/results/<model("survey.survey"):survey>',
        type="http",
        auth="user",
        website=True,
    )
    def survey_report(
        self,
        survey,
        selected_events=None,
        selected_tags=None,
        select_date=None,
        date_end=None,
        answer_token=None,
        **post
    ):

        res = super(SurveyFeedbackEvent, self).survey_report(
            survey,
            answer_token,
        )
        user_input_lines, search_filters = self._extract_survey_data(
            survey,
            selected_events,
            selected_tags,
            select_date,
            date_end,
            post,
        )
        survey_data = survey._prepare_statistics(user_input_lines)
        question_and_page_data = survey.question_and_page_ids._prepare_statistics(
            user_input_lines
        )
        show_date = False
        res.qcontext.update(
            {
                "question_and_page_data": question_and_page_data,
                "survey_data": survey_data,
                "search_filters": search_filters,
                "show_date": show_date,
            }
        )
        user_input_ids = (
            request.env["survey.user_input.line"]
            .sudo()
            .search([("id", "in", user_input_lines.ids)])
            .mapped("user_input_id")
        )


        events = (
            request.env["survey.user_input"]
            .sudo()
            .search([("id", "in", user_input_ids.ids)])
            .mapped("event_id")
        )
        res.qcontext.update({"events": events})

        tags = (
            request.env["survey.user_input"]
            .sudo()
            .search([("id", "in", user_input_ids.ids)])
            .mapped("tag_ids")
        )
        res.qcontext.update({"tags": tags})

        return res

    @http.route(
        "/survey/start/<string:survey_token>/event/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_start_event(
        self, survey_token, event_id=None, answer_token=None, email=False, **post
    ):
        """Start a survey by providing
        * a token linked to a survey;
        * a token linked to an answer or generate a new token if access is allowed;
        """
        # Get the current answer token from cookie
        answer_from_cookie = False
        if not answer_token:
            answer_token = request.httprequest.cookies.get("survey_%s" % survey_token)
            answer_from_cookie = bool(answer_token)

        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=False
        )

        if answer_from_cookie and access_data["validity_code"] in (
            "answer_wrong_user",
            "token_wrong",
        ):
            # If the cookie had been generated for another user or does not correspond
            # to any existing answer object (probably because it has been deleted),
            # ignore it and redo the check. The cookie will be replaced by a legit
            # value when resolving the URL, so we don't clean it further here.
            access_data = self._get_access_data(survey_token, None, ensure_token=False)

        if access_data["validity_code"] is not True:
            return self._redirect_with_error(access_data, access_data["validity_code"])

        survey_sudo, answer_sudo = (
            access_data["survey_sudo"],
            access_data["answer_sudo"],
        )
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer(user=False, email=False)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights("read")
                survey_sudo.with_user(request.env.user).check_access_rule("read")
            except Exception:
                return request.redirect("/")
            else:
                return request.render("survey.survey_403_page", {"survey": survey_sudo})

        if event_id:
            event = request.env["event.event"].sudo().search([("id", "=", event_id)])
            answer_sudo.sudo().write({"event_id": event.id})
            return request.redirect(
                "/survey/%s/%s/event/%s"
                % (survey_sudo.access_token, answer_sudo.access_token, event_id)
            )

    @http.route(
        "/survey/<string:survey_token>/<string:answer_token>/event/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_event_display_page(self, survey_token, answer_token, **post):
        return super(SurveyFeedbackEvent, self).survey_display_page(
            survey_token, answer_token, **post
        )

    # flake8: noqa: C901
    @http.route(
        [
            """/survey/results/<model("survey.survey"):survey>/tag/<string:selected_tags>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/event/<string:selected_events>/tag/<string:selected_tags>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/event/<string:selected_events>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/event/<string:selected_events>/date_start/<string:select_date>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/event/<string:selected_events>/date_start/<string:select_date>/date_end/<string:date_end>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/date_start/<string:select_date>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/date_start/<string:select_date>/event/<string:selected_events>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/date_start/<string:select_date>/date_end/<string:date_end>/event/<string:selected_events>""",  # noqa
            """/survey/results/<model("survey.survey"):survey>/date_start/<string:select_date>/date_end/<string:date_end>""",  # noqa
        ],
        type="http",
        auth="user",
        website=True,
    )
    def survey_report_filter(
        self,
        survey,
        selected_events=None,
        selected_tags=None,
        select_date=None,
        date_end=None,
        answer_token=None,
        **post
    ):

        user_input_lines, search_filters = self._extract_survey_data(
            survey,
            selected_events,
            selected_tags,
            select_date,
            date_end,
            post,
        )
        survey_data = survey._prepare_statistics(user_input_lines)
        question_and_page_data = survey.question_and_page_ids._prepare_statistics(
            user_input_lines
        )
        show_date = False
        readonly_events = False

        template_values = {
            # survey and its statistics
            "survey": survey,
            "question_and_page_data": question_and_page_data,
            "survey_data": survey_data,
            # search
            "search_filters": search_filters,
            "search_finished": post.get("finished") == "true",
        }
        if request.env.user.has_group("survey.group_survey_user"):
            readonly_events = True
            template_values.update({"readonly_events": readonly_events})


        if selected_events:
            select_events = (
                request.env["event.event"]
                .sudo()
                .search([("id", "in", list(map(int, selected_events.split(","))))])
            )
            template_values.update({"select_events": select_events})

            if request.env.user.has_group("survey.group_survey_user"):
                if select_events.user_id != request.env.user:
                    return request.render("website.page_404")


        if selected_tags:
            logging.info(selected_tags);
            select_tags = (
                request.env["event.tag"]
                .sudo()
                .search([("id", "in", list(map(int, selected_tags.split(","))))])
            )
            logging.info(select_tags);
            template_values.update({"select_tags": select_tags})
        #user_input_lines, search_filters = self._extract_filters_data(survey, post)
        user_input_ids = (
            request.env["survey.user_input.line"]
            .sudo()
            .search([("id", "in", user_input_lines.ids)])
            .mapped("user_input_id")
        )

        events = (
            request.env["survey.user_input"]
            .sudo()
            .search([("id", "in", user_input_ids.ids)])
            .mapped("event_id")
        )
        template_values.update({"events": events})

        tags = (
            request.env["survey.user_input"]
            .sudo()
            .search([("id", "in", user_input_ids.ids)])
            .mapped("tag_ids")
        )
        logging.info(tags);
        template_values.update({"tags": tags})

        if select_date:
            show_date = True
            template_values.update({"show_date": show_date})

        if survey.session_show_leaderboard:
            template_values["leaderboard"] = survey._prepare_leaderboard_values()

        return request.render("survey.survey_page_statistics", template_values)
        # flake8: noqa: C901

    # flake8: noqa: C901
    def _extract_survey_data(
        self,
        survey,
        selected_events,
        selected_tags,
        select_date,
        date_end,
        post,
    ):
        search_filters = []
        line_filter_domain, line_choices = [], []
        for data in post.get("filters", "").split("|"):
            try:
                row_id, answer_id = (int(item) for item in data.split(","))
            except:
                pass
            else:
                if row_id and answer_id:
                    line_filter_domain = expression.AND(
                        [
                            [
                                "&",
                                ("matrix_row_id", "=", row_id),
                                ("suggested_answer_id", "=", answer_id),
                            ],
                            line_filter_domain,
                        ]
                    )
                    answers = request.env["survey.question.answer"].browse(
                        [row_id, answer_id]
                    )
                elif answer_id:
                    line_choices.append(answer_id)
                    answers = request.env["survey.question.answer"].browse([answer_id])
                if answer_id:
                    question_id = (
                        answers[0].matrix_question_id or answers[0].question_id
                    )
                    search_filters.append(
                        {
                            "question": question_id.title,
                            "answers": "%s%s"
                            % (
                                answers[0].value,
                                ": %s" % answers[1].value if len(answers) > 1 else "",
                            ),
                        }
                    )
        if line_choices:
            # line_filter_domain = expression.AND([[('suggested_answer_id', '=', line_choices)], line_filter_domain])
            for lc in line_choices:
                line_filter_domain += [
                    ("user_input_line_ids.suggested_answer_id", "=", lc)
                ]
        line_filter_domain += [("test_entry", "=", False)]
        line_filter_domain += [("survey_id", "=", survey.id)]
        if post.get("finished"):
            line_filter_domain += [("state", "=", "done")]
        else:
            line_filter_domain += [("state", "!=", "new")]


        if selected_events:
            select_events = (
                request.env["event.event"]
                .sudo()
                .search([("id", "in", list(map(int, selected_events.split(","))))])
            )
            line_filter_domain += [("event_id", "in", select_events.ids)]

        if selected_tags:
            select_tags = (
                request.env["event.tag"]
                .sudo()
                .search([("id", "in", list(map(int, selected_tags.split(","))))])
            )
            line_filter_domain += [("tag_ids", "in", select_tags.ids)]


        if select_date and not date_end:
            select_date_obj = datetime.strptime(select_date, "%d.%m.%Y")
            select_date_end_obj = select_date_obj + timedelta(
                hours=23, minutes=59, seconds=59
            )
            line_filter_domain += [
                ("create_date", ">=", select_date_obj),
                ("create_date", "<=", select_date_end_obj),
            ]
        if select_date and date_end:
            select_date_start_obj = datetime.strptime(select_date, "%d.%m.%Y")
            select_date_end_obj = datetime.strptime(date_end, "%d.%m.%Y")
            date_end_obj = select_date_end_obj + timedelta(
                hours=23, minutes=59, seconds=59
            )
            line_filter_domain += [
                ("create_date", ">=", select_date_start_obj),
                ("create_date", "<=", date_end_obj),
            ]

        user_input_lines = (
            request.env["survey.user_input"]
            .sudo()
            .search(line_filter_domain)
            .mapped("user_input_line_ids")
        )

        return user_input_lines, search_filters
