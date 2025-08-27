from odoo import _, models

class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    def _get_register_modal_vat_text(self):
        ticket = self
        including_vat = _("inc. VAT")
        website = self.env["website"].get_current_website(fallback=False)
        if website.show_line_subtotals_tax_selection == "tax_excluded":
            return ""
        elif not ticket.product_id.taxes_id.display_name:
            return ""
        else:
            return including_vat + " " + ticket.product_id.taxes_id.display_name
