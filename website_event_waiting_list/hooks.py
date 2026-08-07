##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
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


def post_init_hook(env):
    """Backfill missing waiting-list mail schedulers on install/upgrade.

    ``EventEvent.create``/``write`` only guarantee the two schedulers going
    forward (see ``EventEvent._ensure_waiting_list_mail_schedulers``) - any
    event that already had ``waiting_list`` enabled before this module
    version was installed needs the same backfill run once here, or it
    would keep silently sending no waiting-list mail until someone happens
    to re-save it.
    """
    events = env["event.event"].search([("waiting_list", "=", True)])
    events._ensure_waiting_list_mail_schedulers()
