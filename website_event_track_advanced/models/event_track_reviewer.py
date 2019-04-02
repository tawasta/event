# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventTrackReviewer(models.Model):
    _name = 'event.track.reviewer'
    _inherits = {'res.users': 'user_id'}

    # The point of this class is to provide a subclass between users and review groups
    # Reviewer needs to be an user, but we don't want to add all the extra fields and relations to partner or user
