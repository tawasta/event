# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models
from odoo import _
from odoo.tools import html2plaintext

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = 'event.track'

    # 2. Fields declaration
    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        domain=[('res_model', '=', 'event.track')],
        string='Attachments',
    )
    description_original = fields.Html(
        string='Original description',
        readonly=True,
    )

    rating = fields.Selection([
        ('0', 'Not rated'),
        ('1', 'Weak'),
        ('2', 'Decent'),
        ('3', 'Good'),
        ('4', 'Great')
        ('5', 'Excellent')
    ],
        select=True,
        string='Rating',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, values):
        values['description_original'] = values.get('description')

        return super(EventTrack, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('description'):
            old_desc = html2plaintext(self.description).splitlines()
            new_desc = html2plaintext(values['description']).splitlines()

            d = difflib.Differ()
            diff = d.compare(old_desc, new_desc)

            diff_msg = ''

            for line in diff:
                code = line[:2]
                text = line[2:]

                if code in ['+ ', '- ']:
                    if code == '+ ':
                        line_number = new_desc.index(text)
                        css_style = 'color: #0275d8;'
                    else:
                        line_number = old_desc.index(text)
                        css_style = 'color: #636c72;'

                    line_number += 1

                    if not text.isspace() and text.strip() != '':
                        diff_msg += '<span style="%s">%s: %s</span><br/>' % (css_style, line_number, text)

            if diff_msg != '':
                subject = _('Content modified')

                body = '<strong>' + subject + '</strong><br/>' +\
                       '<p>' + diff_msg + '</p>'

                self.message_post(
                    subject=subject,
                    body=body,
                )

        return super(EventTrack, self).write(values)

    # 7. Action methods

    # 8. Business methods
