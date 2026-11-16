import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

/**
 * Shows a check mark in the selected event tags and a plus sign in the others,
 * so that the state of a tag does not depend on its colour only.
 */
export class EventInterestTags extends Interaction {
    static selector = ".o_event_interest_tags";
    dynamicContent = {
        ".btn-check": {
            "t-on-change.noUpdate.withTarget": this.onTagChange,
        },
    };

    start() {
        // The browser can restore the checkboxes after a reload or a back navigation
        // without a change event, so the icons are set from the actual state
        for (const checkboxEl of this.el.querySelectorAll(".btn-check")) {
            this.syncIcon(checkboxEl);
        }
    }

    onTagChange(ev, currentTargetEl) {
        this.syncIcon(currentTargetEl);
    }

    syncIcon(checkboxEl) {
        const iconEl = checkboxEl.nextElementSibling?.querySelector(
            ".o_event_interest_tag_icon"
        );
        if (!iconEl) {
            return;
        }
        iconEl.classList.toggle("fa-check", checkboxEl.checked);
        iconEl.classList.toggle("fa-plus", !checkboxEl.checked);
    }
}

registry
    .category("public.interactions")
    .add("event_notification_subscription.event_interest_tags", EventInterestTags);
