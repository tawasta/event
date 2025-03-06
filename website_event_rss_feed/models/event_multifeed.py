from werkzeug import urls

from odoo import api, fields, models


class WebsiteEventMultifeed(models.Model):
    _name = "event.multifeed"
    _description = "Event RSS Multifeed"
    _order = "name"

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    name = fields.Char("Name", required=True, translate=True)
    description = fields.Text("Description", translate=True)
    feed_url = fields.Char("Feed URL", readonly=1, compute="_compute_feed_url")
    lang = fields.Selection(
        required=True,
        selection=_get_lang,
        string="Language",
        help="Events will be shown in this language in the RSS feed",
    )
    event_tag_ids = fields.Many2many(
        "event.tag",
        string="Event Tags",
        help="Event Tags to include into this multifeed",
        index=True,
    )

    def _compute_feed_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for feed in self:
            feed.feed_url = urls.url_join(base_url, "/event-feed/%s" % feed.id)
