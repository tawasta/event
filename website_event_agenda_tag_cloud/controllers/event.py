from odoo import http, fields, _
from odoo.http import request


class WebsiteEvent(http.Controller):

    @http.route(
        '/event/get/keywords',
        type='json',
        auth='public',
        website=True)
    def event_get_keywords(self, **post):
        # Get keywords
        event_id = post.get('event_id')
        EventEvent = request.env['event.event']
        EventTrack = request.env['event.track']

        res = dict()
        keywords = list()

        if event_id:
            event = EventEvent.sudo().browse([int(event_id)])

            for tag in event.allowed_track_tag_ids:
                # TODO: a stored field. This is very heavy
                weight = EventTrack.search_count([
                    ('event_id', '=', event.id),
                    ('tag_ids', '=', tag.id),
                ])

                keywords.append(dict(
                    text=tag.name,
                    weight=weight,
                    html={
                        'data-keyword-id': tag.id,
                        'class': 'keyword-clickable',
                    },
                    link='?keyword-id=%s' % tag.id,
                ))

            res['keywords'] = keywords

        return res
