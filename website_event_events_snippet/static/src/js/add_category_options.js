odoo.define("website_event_events_snippet.add_category_options", function (require) {
    "use strict";

    var sOptions = require("web_editor.snippets.options");

    sOptions.registry.js_get_category_list = sOptions.Class.extend({
        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * @override
         */
        _renderCustomXML: function (uiFragment) {
            return this._rpc({
                model: "event.event",
                method: "search_read",
                args: [[["tag_ids", "!=", false]], ["tag_ids"]],
            }).then((events) => {
                const tagSet = new Set();

                // Extract unique tags from events
                for (const event of events) {
                    const tags = event.tag_ids;
                    for (const tagId of tags) {
                        tagSet.add(tagId);
                    }
                }

                const tagIdsArray = Array.from(tagSet);

                return this._rpc({
                    model: "event.tag",
                    method: "read",
                    args: [tagIdsArray, ["name"]],
                }).then((tagNames) => {
                    const menuEl = uiFragment.querySelector(
                        '[name="category_selection"]'
                    );
                    for (const categ of tagNames) {
                        const el = document.createElement("we-button");
                        el.dataset.selectDataAttribute = categ.id;
                        el.textContent = categ.name;
                        menuEl.appendChild(el);
                    }
                });
            });
        },
    });
});
