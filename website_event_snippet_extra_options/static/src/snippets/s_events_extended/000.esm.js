/** @odoo-module **/

// eslint-disable-next-line no-unused-vars
import DynamicSnippet from "@website/snippets/s_dynamic_snippet/000";
import publicWidget from "@web/legacy/js/public/public_widget";

/* Website_event's DynamicSnippetEvents does not expose itself with "export",
so it seems fetching it via publicWidget.registry is needed to extend its
functionality? */
const OriginalDynamicSnippetEvents = publicWidget.registry.events;

const PatchedDynamicSnippetEvents = OriginalDynamicSnippetEvents.extend({
    init: function () {
        this._super.apply(this, arguments);
    },

    /**
     * Apply additional search criteria to the dynamic widget based on the
     * snippet configuration
     *
     * @returns combined search domain
     */
    _getSearchDomain: function () {
        let searchDomain = this._super.apply(this, arguments);

        // Always exclude private events
        searchDomain = searchDomain.concat([["is_private_event", "=", false]]);

        // Check the configured timeframe criteria
        const eventTimeframe = this.$el.get(0).dataset.eventTimeframe;

        // eslint-disable-next-line no-undef
        const currentDate = luxon.DateTime.now();

        switch (eventTimeframe) {
            case "past":
                searchDomain = searchDomain.concat([["date_begin", "<", currentDate]]);
                break;
            case "upcoming":
                searchDomain = searchDomain.concat([["date_begin", ">=", currentDate]]);
                break;
            default:
                break;
        }

        // Check the configured promotion criteria
        const eventPromotedOnly = this.$el.get(0).dataset.eventPromotedOnly;

        if (eventPromotedOnly) {
            searchDomain = searchDomain.concat([["is_promoted", "=", true]]);
        }

        return searchDomain;
    },
});

publicWidget.registry.events = PatchedDynamicSnippetEvents;
