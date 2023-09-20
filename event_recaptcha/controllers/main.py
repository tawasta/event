# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.http import request
import logging


class WebsiteEventCaptchaController(WebsiteEventSaleController):

    @http.route()
    def registration_confirm(self, event, **post):
        referer = request.httprequest.headers.get('Referer')
        base_url = http.request.httprequest.url_root
        if referer and str(base_url) not in referer:
            raise request.not_found()
        else:
            res = super(WebsiteEventCaptchaController, self).registration_confirm(event, **post)

            return res

    @http.route()
    def registration_new(self, event, **post):
        referer = request.httprequest.headers.get('Referer')
        base_url = http.request.httprequest.url_root

        if referer and str(base_url) not in referer:
            raise request.not_found()
        else:
            res = super(WebsiteEventCaptchaController, self).registration_new(event, **post)

            return res

