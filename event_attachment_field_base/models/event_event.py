from odoo import api, models


class EventEvent(models.Model):
    _inherit = "event.event"

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        events._link_attachments(self._get_linked_attachment_fields())
        return events

    def write(self, vals):
        res = super().write(vals)
        changed_fields = [
            field_name
            for field_name in self._get_linked_attachment_fields()
            if vals.get(field_name)
        ]
        if changed_fields:
            self._link_attachments(changed_fields)
        return res

    @api.model
    def _get_linked_attachment_fields(self):
        """Return the ir.attachment Many2one fields to link to their event.

        Attachment field modules extend this with their own field name.
        """
        return []

    def _link_attachments(self, field_names):
        """Link the user's own unlinked attachments to their event.

        An attachment without res_id can be modified only by its creator.
        Linking it to the event makes its access follow the event's access
        rights instead, so any user who can edit the event can replace the file.
        """
        for event in self:
            for field_name in field_names:
                attachment = event[field_name]
                if not attachment or attachment.res_id or attachment.res_field:
                    continue
                # Never re-parent an attachment that belongs to another model
                if attachment.res_model not in (False, self._name):
                    continue
                # Linking someone else's file would hand it over to this event
                if attachment.create_uid != self.env.user:
                    continue
                attachment.write({"res_model": self._name, "res_id": event.id})
