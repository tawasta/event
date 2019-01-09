# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2017 Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    'name': 'Advanced event tracks',
    'summary': 'An advanced event tracks process',
    'version': '10.0.1.17.3',
    'category': 'Events',
    'website': 'http://www.tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [
            'difflib'
        ],
        'bin': [],
    },
    'depends': [
        'auth_signup',
        'document',
        'event',
        'event_image',
        'partner_firstname',
        'report',
        'website_event_track',
        'website_event_track_disable_translate',
        'website_event_track_image',
        'website_event_track_mass_mailing',
        'website_utilities',
    ],
    'data': [
        'data/email_template_event_track_announced.xml',
        'data/email_template_event_track_refused.xml',
        'data/event_track_type.xml',
        'data/report_paperformat_data.xml',

        'reports/event_track_location_schedule_report.xml',
        'reports/event_track_rating_comment_report.xml',
        'reports/event_track_rating_report.xml',
        'reports/event_track_report.xml',
        'reports/event_track_reviewer_report.xml',
        'reports/event_track_signpost.xml',

        'security/event_track_security.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',

        'views/event_event_form.xml',

        'views/event_track_form.xml',
        'views/event_track_form_portal.xml',
        'views/event_track_kanban.xml',
        'views/event_track_location_form.xml',
        'views/event_track_location_tree.xml',
        'views/event_track_menu.xml',

        'views/event_track_rating.xml',
        'views/event_track_rating_form.xml',
        'views/event_track_rating_search.xml',
        'views/event_track_rating_tree.xml',

        'views/event_track_review_group.xml',

        'views/event_track_reviewer_tree.xml',
        'views/event_track_reviewer.xml',

        'views/event_track_search.xml',
        'views/event_track_tag.xml',
        'views/event_track_target_group.xml',
        'views/event_track_tree.xml',
        'views/event_track_type.xml',

        'views/website_event_assets.xml',
        'views/website_event_track_agenda.xml',
        'views/website_event_track_application.xml',

        'views/website_event_track_poster.xml',
        'views/website_event_track_proposal.xml',
        'views/website_event_track_proposal_success.xml',
        'views/website_event_track_tracks.xml',
        'views/website_event_track_view.xml',
        'views/website_event_track_workshop.xml',

        'wizards/event_track_assign_wizard.xml',
    ],
    'demo': [
    ],
}
