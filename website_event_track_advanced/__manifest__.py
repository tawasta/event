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
    'version': '10.0.1.1.16',
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
        'document',
        'event',
        'partner_firstname',
        'website_event_track',
    ],
    'data': [
        'data/event_track_type.xml',

        'security/event_track_security.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',

        'views/event_event_form.xml',
        'views/event_track_form.xml',
        'views/event_track_form_portal.xml',
        'views/event_track_kanban.xml',
        'views/event_track_review_group.xml',
        'views/event_track_search.xml',
        'views/event_track_tag.xml',
        'views/event_track_target_group.xml',
        'views/event_track_tree.xml',
        'views/event_track_type.xml',

        'views/website_event_assets.xml',
        'views/website_event_track_agenda.xml',
        'views/website_event_track_application.xml',
        'views/website_event_track_proposal.xml',
        'views/website_event_track_proposal_success.xml',

        'wizards/event_track_assign_wizard.xml',
    ],
    'demo': [
    ],
}
