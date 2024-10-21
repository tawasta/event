import json
import secrets
from collections import defaultdict
from datetime import datetime

from odoo import _, http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class EventRegistrationController(WebsiteEventController):
    def _process_tickets_form(self, event, form_details):
        tickets = super(EventRegistrationController, self)._process_tickets_form(
            event, form_details
        )

        for ticket in tickets:
            other_ticket_name = "other_nb_register-%s" % ticket["id"]

            if other_ticket_name in form_details:
                ticket["is_inviting_others"] = True

        return tickets

    @http.route()
    def registration_new(self, event, **post):
        tickets = self._process_tickets_form(event, post)

        # Tarkista, kutsutaanko muita
        if any(ticket.get("is_inviting_others") for ticket in tickets):
            draft_registrations = []
            order_sudo = request.website.sale_get_order(force_create=True)
            if order_sudo.state != "draft":
                request.website.sale_reset()
                order_sudo = request.website.sale_get_order(force_create=True)

            tickets_data = defaultdict(int)
            for ticket in tickets:
                if ticket["is_inviting_others"]:
                    tickets_data[ticket["ticket"].id] += ticket["quantity"]

            cart_data = {}
            for ticket_id, count in tickets_data.items():
                ticket_sudo = request.env["event.event.ticket"].sudo().browse(ticket_id)
                cart_values = order_sudo._cart_update(
                    product_id=ticket_sudo.product_id.id,
                    add_qty=count,
                    event_ticket_id=ticket_id,
                )
                cart_data[ticket_id] = cart_values["line_id"]

            for ticket in tickets:
                if ticket["is_inviting_others"]:
                    registration = (
                        request.env["event.registration"]
                        .sudo()
                        .create(
                            {
                                "event_id": event.id,
                                "name": "Draft Registration",
                                "state": "draft",
                                "event_ticket_id": ticket["ticket"].id,
                                "sale_order_id": order_sudo.id,
                                "sale_order_line_id": cart_data[ticket["ticket"].id],
                                "invite_others": True,
                            }
                        )
                    )
                    draft_registrations.append(registration)

            request.session["website_sale_cart_quantity"] = order_sudo.cart_quantity

            return {"redirect": "/shop/checkout"}

        return super(EventRegistrationController, self).registration_new(event, **post)

    @http.route(
        ["/send/invitation"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def send_invitation(self, **post):
        registration_id = post.get("registration_id")
        if not registration_id:
            return json.dumps(
                {"status": "error", "message": "Registration ID is missing"}
            )

        registration = (
            request.env["event.registration"]
            .sudo()
            .search([("id", "=", int(registration_id))], limit=1)
        )

        if not registration:
            return json.dumps({"status": "error", "message": "Registration not found"})

        invite_email = post.get("invite_email")
        if not invite_email:
            return json.dumps({"status": "error", "message": "No email provided"})

        invite_tracker = (
            request.env["registration.invitation"]
            .sudo()
            .create(
                {
                    "registration_id": registration.id,
                    "invite_email": invite_email,
                    "invited_date": datetime.now(),
                    "is_used": False,
                    "access_token": secrets.token_urlsafe(32),
                }
            )
        )

        registration.sudo().write({"invite_id": invite_tracker.id})

        mail_template = request.env.ref(
            "event_ticket_purchase_options.event_invitation_email_template"
        )
        if not mail_template:
            return json.dumps(
                {"status": "error", "message": "Email template not found"}
            )

        email_values = {
            "email_to": invite_email,
            "auto_delete": True,
            "message_type": "email",
            "recipient_ids": [],
            "partner_ids": [],
        }

        try:
            mail_template.send_mail(
                registration.id,
                force_send=True,
                raise_exception=True,
                email_values=email_values,
            )
            body = f"An invitation has been sent to the email address: {invite_email}."
            registration.sudo().message_post(
                body=body,
                subject=_("Invitation sent"),
                subtype_xmlid="mail.mt_note",
                message_type="notification",
            )

        except Exception as e:
            return json.dumps(
                {"status": "error", "message": f"Failed to send invitation: {str(e)}"}
            )

        return json.dumps(
            {
                "status": "success",
                "message": "Invitation sent",
                "invite_id": invite_tracker.id,
            }
        )

    @http.route(
        ["/event/<int:event_id>/invitation/<int:invite_id>/accept"],
        type="http",
        auth="public",
        website=True,
    )
    def accept_invitation(self, event_id, invite_id, access_token=None, **post):
        invitation = (
            request.env["registration.invitation"]
            .sudo()
            .search([("id", "=", invite_id)], limit=1)
        )

        if not invitation or invitation.access_token != access_token:
            return request.render("website.403")

        event = (
            request.env["event.event"].sudo().search([("id", "=", event_id)], limit=1)
        )
        if not event:
            return request.render("website.403")

        if invitation.is_used:
            values = {
                "invitation": invitation,
                "event": event,
                "show_thank_you": True,
            }
            return request.render(
                "event_ticket_purchase_options.event_invitation_form", values
            )

        values = {
            "invitation": invitation,
            "event": event,
            "counter": 1,
        }

        return request.render(
            "event_ticket_purchase_options.event_invitation_form", values
        )

    # flake8: noqa: C901
    @http.route(
        ["/accept_invitation"], type="http", auth="public", website=True, csrf=True
    )
    def accept_invitation_form(self, **post):
        invite_data = {
            "invite_id": post.pop("invite_id", None),
            "access_token": post.pop("access_token", None),
            "event_id": post.pop("event_id", None),
            "return_url": post.pop("return_url", None),
        }
        privacy_vals = {
            key: post.pop(key)
            for key in list(post.keys())
            if key.startswith("privacy_")
        }
        invitation = (
            request.env["registration.invitation"]
            .sudo()
            .search([("id", "=", invite_data["invite_id"])], limit=1)
        )
        form_details = self._sort_form_details(post)

        for invitation.registration_id, form_detail in zip(
            invitation.registration_id, form_details.values()
        ):
            invitation.registration_id.process_survey(
                invitation.registration_id.id, form_detail, privacy_vals
            )

        invitation.sudo().write(
            {
                "is_used": True,
                "used_date": datetime.now(),
            }
        )

        return_url = f"{invite_data['return_url']}?access_token={invite_data['access_token']}&thank_you=1"

        return request.redirect(return_url)
