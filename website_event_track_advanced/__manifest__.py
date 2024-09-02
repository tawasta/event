##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

{
    "name": "Website Event Track Advanced",
    "summary": "Advanced features for Event Track",
    "version": "17.0.1.0.0",
    "category": "Events",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "portal",
        "website_event_track",
        "website_event_track_manager_proposal",
        "partner_firstname",
        "web_content_link_url",
        "website_forum",
    ],
    "data": [
        "data/email_template_data.xml",
        "data/event_track_rating_grade_data.xml",
        #"data/event_track_stage_data.xml",
        "data/event_track_type_data.xml",
        "security/ir.model.access.csv",
        "security/event_track_security.xml",
        "wizards/event_track_assign_wizard.xml",
        #"views/assets.xml",
        #"views/res_config_settings_view.xml",
        "views/event_track_rating_views.xml",
        "views/event_track_views.xml",
        "views/event_track_reviewer_views.xml",
        "views/event_track_review_group_views.xml",
        "views/event_track_location_views.xml",
        "views/event_track_type_views.xml",
        "views/event_track_tag_views.xml",
        "views/event_track_target_group_views.xml",
        "views/event_track_speaker.xml",
        "views/event_track_stage_views.xml",
        "views/event_views.xml",
        "views/event_menus.xml",
        "views/event_track_templates_proposal.xml",
        "views/event_track_templates_page.xml",
        "views/event_track_templates_agenda.xml",
        "views/event_track_templates_list.xml",
        "views/portal_templates.xml",
        "report/event_track_location_schedule_report.xml",
        "report/report_menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_event_track_advanced/static/src/js/track_proposal.esm.js",
        ],
    },
}
