import logging

from odoo import fields, http
from odoo.http import request
from odoo.tools import html2plaintext

from odoo.addons.website.controllers.main import Website

_logger = logging.getLogger(__name__)


class WebsiteEventRssMultifeed(Website):
    @http.route(
        ["""/event-feed/<model("event.multifeed"):multifeed>"""],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def event_multi_feed(self, multifeed, limit="15", **kwargs):
        # Get events belonging to the tags configured in the multifeed.

        multifeed_events = (
            request.env["event.event"]
            .with_context(lang=multifeed.lang or "en_US")
            .search(
                [
                    ("tag_ids", "in", multifeed.event_tag_ids.ids),
                    ("is_published", "=", True),
                    ("date_begin", ">=", fields.Datetime.now()),
                ],
                limit=min(int(limit), 50),
                order="date_begin ASC",
            )
        )

        v = {}
        v["multifeed"] = multifeed
        v["base_url"] = multifeed.get_base_url()
        v["events"] = multifeed_events
        v["html2plaintext"] = html2plaintext

        # Get the event with latest write date to be used as the <updated> element
        v["last_updated_event"] = (
            max(multifeed_events, key=lambda e: e.write_date)
            if multifeed_events
            else None
        )

        v["event_images"] = {}

        for event in multifeed_events:

            # this mixin function returns either "none" or "url('path-to-image')"
            event_background = event._get_background()

            if event_background != "none":
                try:

                    # strip out the "url('" and "')" parts
                    event_image_path = event._get_background()[4:-1].strip("'")

                    # If the event is still using the default jpg images, e.g.
                    # /website_event/static/src/img/event_cover_4.jpg
                    # it can be used as is without further processing.

                    if event_image_path.startswith("/website_event/static/src/img/"):
                        image_info = {
                            "image_url": multifeed.get_base_url() + event_image_path,
                            "image_mimetype": "image/jpeg",
                        }
                    else:
                        # If a custom image was added via website builder,
                        # find the attachment record so we can read the image mimetype.
                        # path is in the form of /web/image/100231-<imagefilename>.<extension>
                        split_path = event_image_path.split("/")

                        attachment_id = split_path[3].split("-")[0]

                        image_attachment = (
                            request.env["ir.attachment"]
                            .sudo()
                            .search([["id", "=", attachment_id]])
                            .ensure_one()
                        )

                        image_info = {
                            "image_url": multifeed.get_base_url() + event_image_path,
                            "image_mimetype": image_attachment.mimetype,
                        }

                    v["event_images"][event.id] = image_info

                except Exception as e:
                    _logger.error(
                        "Could not get image URL and mimetype for event ID %s. "
                        "Attempted to parse %s. Details: "
                        % (event.id, event._get_background())
                    )
                    _logger.error(str(e))
                    continue

        r = request.render(
            "website_event_rss_feed.event_multifeed",
            v,
            headers=[("Content-Type", "application/atom+xml")],
        )
        return r
