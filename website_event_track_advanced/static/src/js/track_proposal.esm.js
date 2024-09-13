/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {loadWysiwygFromTextarea} from "@web_editor/js/frontend/loadWysiwygFromTextarea"; // WYSIWYG loader import
import {jsonrpc} from "@web/core/network/rpc_service"; // Jsonrpc import
import Dialog from "@web/legacy/js/core/dialog";
import {_t} from "@web/core/l10n/translation";
// Import {renderToElement} from "@web/core/utils/render";
// Import { qweb } from 'web.core';

publicWidget.registry.TrackProposalFormInstance = publicWidget.Widget.extend({
    selector: "#modal_event_track_application",

    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this._bindTypeChange();
        this._enableWysiwyg(); // Enable WYSIWYG editor
        this._loadTrackData(); // Load track data when modal is opened
        this._clearFormOnClose(); // Clear form when modal is closed
        this._bindFormSubmit(); // Bindataan lomakkeen submit AJAX-pyyntöön
        this._bindAddSpeaker();
        this._bindRemoveSpeaker();
        this._removeAttachments();
        this._setupModalCloseBehavior(); // Setup custom modal close behavior
    },

    _bindRemoveSpeaker: function () {
        const container = $(".track-application-speakers-div-container");

        // Päivitetään puhujien indeksit ja numerot (ensimmäistä riviä ei kosketa)
        function _updateSpeakerIndexes() {
            const rows = container.find(
                ".track-application-speakers-div-row-container"
            );

            // Aloitetaan toisesta rivistä (index 1), jolloin ensimmäistä riviä ei muuteta
            rows.slice(1).each(function (index, row) {
                const speakerCount = index + 2; // Numerointi alkaa 2:sta, koska index alkaa 1:stä (ensimmäistä riviä ei kosketa)
                const $row = $(row);

                // Päivitetään numero ja id-attribuutit
                $row.find(".presenter-span").text(`Presenter #${speakerCount}`);

                // Päivitetään kenttien name- ja id-attribuutit
                $row.find("input, label").each(function () {
                    const elem = $(this);
                    const nameAttr = elem.attr("name");
                    const forAttr = elem.attr("for");

                    if (nameAttr) {
                        elem.attr(
                            "name",
                            nameAttr.replace(/\[\d+\]/, `[${speakerCount}]`)
                        );
                    }
                    if (forAttr) {
                        elem.attr(
                            "for",
                            forAttr.replace(/\[\d+\]/, `[${speakerCount}]`)
                        );
                    }
                });
            });
        }

        // Käytetään delegoitua tapahtumankuuntelijaa, jotta myös kloonatut elementit saavat tapahtuman
        container.on("click", ".btn-remove-speaker", function (event) {
            event.preventDefault(); // Estä oletustoiminto

            const $row = $(this).closest(
                ".track-application-speakers-div-row-container"
            ); // Viittaus rivin kontaineriin
            const speaker_id = $row.find("input[name^='speaker_id']").val();
            console.log(speaker_id);

            // Näytä vahvistusdialogi
            Dialog.confirm(this, _t("Are you sure you want to remove this speaker?"), {
                title: _t("Confirm Removal"),
                size: "medium",
                confirm_callback: function () {
                    $row.remove();

                    // Päivitetään puhujien indeksit ja numerot
                    _updateSpeakerIndexes();

                    // Päivitetään puhujien lukumäärä
                    var speaker_count =
                        Number($("#track-application-speaker-input-index").val()) - 1;
                    $("#track-application-speaker-input-index").val(speaker_count);
                },
            });
        });
    },

    _setupModalCloseBehavior: function () {
        // Estä modaalin sulkeutuminen ulkopuolisista klikkauksista tai Esc-näppäimen painalluksesta
        $("#modal_event_track_application").modal({
            backdrop: "static",
            keyboard: false,
        });

        // Lisää sulkemispainikkeille toiminnallisuus
        $(".close.warning-close-modal, .btn.btn-secondary.warning-close-modal").click(
            function () {
                // Näytä vahvistusviesti käyttäjälle
                Dialog.confirm(
                    this,
                    _t(
                        "If you close the form now, any unsaved changes will be lost. Do you really want to close?"
                    ),
                    {
                        title: _t("Confirm close"),
                        size: "medium",
                        confirm_callback: function () {
                            $("#track-application-form")[0].reset();
                            location.reload(); // Päivitä sivu
                        },
                    }
                );
            }
        );
    },

    _removeAttachments: function () {
        $("#clear-attachment").click(function () {
            $("#attachment_ids").val(""); // Tyhjennä liiteinput
        });
        // Tämä funktio käsittelee liitteiden poistamisen merkitsemisen
        $(".remove-attachment").click(function () {
            const attachmentId = $(this).data("id");
            const attachmentDiv = $(`#attachment-${attachmentId}`);

            // Lisätään poistettava liite hidden-kenttään
            const removeInput = $("#remove_attachments_input");
            const currentValues = removeInput.val() ? removeInput.val().split(",") : [];
            if (!currentValues.includes(attachmentId.toString())) {
                currentValues.push(attachmentId);
                removeInput.val(currentValues.join(","));
            }

            // Merkitään visuaalisesti poistetuksi, mutta ei vielä poisteta
            attachmentDiv.css("opacity", "0.5"); // Vähennetään näkyvyyttä osoittaen, että liite on merkitty poistettavaksi
            $(this).prop("disabled", true).text("Marked for Removal");
        });
    },

    _renderSpeakers: function (speakers) {
        const container = $(".track-application-speakers-div-container");
        const firstRow = container.find(
            ".track-application-speakers-div-row-container:first"
        );

        // Ensimmäinen puhuja asetetaan olemassa oleviin kenttiin
        if (speakers.length > 0) {
            const firstSpeaker = speakers[0];
            firstRow.find(".presenter-span").text(`Presenter #1`);
            firstRow
                .find("input[name^='speaker_firstname']")
                .val(firstSpeaker.firstname);
            firstRow.find("input[name^='speaker_lastname']").val(firstSpeaker.lastname);
            firstRow.find("input[name^='speaker_email']").val(firstSpeaker.email);
            firstRow.find("input[name^='speaker_phone']").val(firstSpeaker.phone);
            firstRow
                .find("input[name^='speaker_organization']")
                .val(firstSpeaker.organization);
            firstRow.find("input[name^='speaker_title']").val(firstSpeaker.title);
            firstRow.find("input[name^='speaker_id']").val(firstSpeaker.id);
        }

        let speakerCount = 1;

        // Loput puhujat lisätään kloonaamalla ensimmäinen rivi
        speakers.slice(1).forEach((speaker, index) => {
            speakerCount = index + 2; // Aloitetaan laskeminen 2:sta

            const newRow = firstRow.clone();
            newRow.attr("id", speakerCount);

            // Päivitetään kenttien arvot
            newRow.find(".presenter-span").text(`Presenter #${speakerCount}`);
            newRow.find("input[name^='speaker_id']").val(speaker.id);
            newRow.find("input[name^='speaker_firstname']").val(speaker.firstname);
            newRow.find("input[name^='speaker_lastname']").val(speaker.lastname);
            newRow.find("input[name^='speaker_email']").val(speaker.email);
            newRow.find("input[name^='speaker_phone']").val(speaker.phone);
            newRow
                .find("input[name^='speaker_organization']")
                .val(speaker.organization);
            newRow.find("input[name^='speaker_title']").val(speaker.title);

            // Päivitetään kenttien id:t ja name-attribuutit oikeiksi
            newRow
                .find("label[for^='speaker_firstname']")
                .attr("for", `speaker_firstname[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_firstname']")
                .attr("name", `speaker_firstname[${speakerCount}]`);
            newRow
                .find("label[for^='speaker_lastname']")
                .attr("for", `speaker_lastname[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_lastname']")
                .attr("name", `speaker_lastname[${speakerCount}]`);
            newRow
                .find("label[for^='speaker_email']")
                .attr("for", `speaker_email[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_email']")
                .attr("name", `speaker_email[${speakerCount}]`);
            newRow
                .find("label[for^='speaker_phone']")
                .attr("for", `speaker_phone[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_phone']")
                .attr("name", `speaker_phone[${speakerCount}]`);
            newRow
                .find("label[for^='speaker_organization']")
                .attr("for", `speaker_organization[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_organization']")
                .attr("name", `speaker_organization[${speakerCount}]`);
            newRow
                .find("label[for^='speaker_title']")
                .attr("for", `speaker_title[${speakerCount}]`);
            newRow
                .find("input[name^='speaker_title']")
                .attr("name", `speaker_title[${speakerCount}]`);

            // Poista "disabled" attribuutti "Remove speaker" -painikkeesta kloonatuilla riveillä
            newRow.find(".btn-remove-speaker").removeAttr("disabled");

            container.append(newRow);
        });

        // Päivitetään piilotettu input, joka seuraa puhujien lukumäärää
        $("#track-application-speaker-input-index").val(speakerCount);
    },

    _loadTrackData: function () {
        const self = this;
        $("#modal_event_track_application").on("show.bs.modal", function (event) {
            $("#track-application-form")[0].reset();
            var button = $(event.relatedTarget);
            var trackId = button.data("track-id"); // Get track ID from button
            var eventId = button.data("event-id"); // Hae event ID napista
            var isReview = button.data("review") || false; // Tarkistetaan, onko kyseessä arvostelutila

            // Määritä action URL ja aseta se lomakkeelle
            var actionUrl = `/event/${eventId}/track_proposal/post`;
            $("#track-application-form").attr("action", actionUrl);

            if (!trackId) {
                // Jos trackId ei ole määritelty, hae eventin track_types_ids
                jsonrpc("/event/application_types", {
                    event_id: eventId,
                }).then((response) => {
                    if (response.contact_info) {
                        $('input[name="contact_firstname"]').val(
                            response.contact_info.firstname
                        );
                        $('input[name="contact_lastname"]').val(
                            response.contact_info.lastname
                        );
                        $('input[name="contact_email"]').val(
                            response.contact_info.email
                        );
                        $('input[name="contact_phone"]').val(
                            response.contact_info.phone
                        );
                        $('input[name="contact_organization"]').val(
                            response.contact_info.organization
                        );
                        $('input[name="contact_title"]').val(
                            response.contact_info.title
                        );
                        $('input[name="contact_id"]').val(
                            response.contact_info.contact_id
                        );
                    }
                    self._populateSelectOptions("type", response.application_types);
                    if (response.multiple_target_groups) {
                        $(".target-groups-select")
                            .attr("multiple", "multiple")
                            .select2({
                                maximumSelectionSize: 3,
                            });
                    }
                    self._populateSelectOptions(
                        "target_groups",
                        response.target_groups
                    );

                    if (response.multiple_tags) {
                        $(".tags-select").attr("multiple", "multiple").select2({
                            maximumSelectionSize: 3,
                        });
                    }
                    self._populateSelectOptions("tags", response.tags);
                    self._populateSelectOptions("request_time", response.request_time);
                    self._populateSelectOptions("language", response.languages);

                    const privacyDIV = $("#privacy-acceptance-container");
                    privacyDIV.removeClass("d-none");

                    self._enableWysiwyg([
                        {selector: 'textarea[name="description"]'},
                        {selector: 'textarea[name="target_group_info"]'},
                        {selector: 'textarea[name="extra_info"]'},
                        // {selector: 'textarea[name="workshop_goals"]'},
                        // {selector: 'textarea[name="workshop_schedule"]'},
                        {selector: 'textarea[name="webinar_info"]'},
                    ]);

                    $("#application-submit-button-send")
                        .attr("name", "track-confirm")
                        .val("track-confirm");
                });
            } else {
                // Hae tiedot tietylle trackille
                jsonrpc("/event/track/data", {
                    track_id: trackId,
                    isReview: isReview,
                }).then((trackData) => {
                    self._populateSelectOptions(
                        "type",
                        trackData.application_types,
                        trackData.type
                    );

                    if (trackData.multiple_tags) {
                        $(".tags-select").attr("multiple", "multiple");
                        self._populateSelectOptions("tags", trackData.tags);
                        $(".tags-select").val(trackData.tag_ids).select2({
                            maximumSelectionSize: 3,
                        });
                    } else {
                        self._populateSelectOptions(
                            "tags",
                            trackData.tags,
                            trackData.tag_ids
                        );
                    }

                    if (trackData.attachments && trackData.attachments.length > 0) {
                        let attachmentList = "";
                        trackData.attachments.forEach(function (attachment) {
                            attachmentList += `
                                <div id="attachment-${attachment.id}" class="o_track_proposal_attachment">
                                    <a href="/web/content/${attachment.id}" target="_blank">${attachment.name}</a>
                                    <button class="btn btn-danger btn-sm remove-attachment" data-id="${attachment.id}">Remove</button>
                                </div>`;
                        });
                        $("#existing_attachments").html(attachmentList);

                        // Bindataan poiston merkitseminen
                        self._removeAttachments();
                    }

                    self._populateSelectOptions(
                        "language",
                        trackData.languages,
                        trackData.language
                    );

                    if (trackData.multiple_target_groups) {
                        $(".target-groups-select").attr("multiple", "multiple");
                        self._populateSelectOptions(
                            "target_groups",
                            trackData.target_groups
                        );
                        $(".target-groups-select")
                            .val(trackData.target_group_ids)
                            .select2({
                                maximumSelectionSize: 3,
                            });
                    } else {
                        self._populateSelectOptions(
                            "target_groups",
                            trackData.target_groups,
                            trackData.target_group_ids
                        );
                    }

                    $('input[name="track_id"]').val(trackData.track_id);
                    $('input[name="name"]').val(trackData.name);
                    $('input[name="video_url"]').val(trackData.video_url);

                    $('input[name="contact_firstname"]').val(
                        trackData.contact.firstname
                    );
                    $('input[name="contact_lastname"]').val(trackData.contact.lastname);
                    $('input[name="contact_email"]').val(trackData.contact.email);
                    $('input[name="contact_phone"]').val(trackData.contact.phone);
                    $('input[name="contact_organization"]').val(
                        trackData.contact.organization
                    );
                    $('input[name="contact_title"]').val(trackData.contact.title);
                    $('input[name="contact_id"]').val(trackData.contact.id);

                    $("#description_readonly").html(trackData.description);
                    $("#target_group_info_readonly").html(trackData.target_group_info);
                    $("#extra_info_readonly").html(trackData.extra_info);
                    $("#workshop_goals_readonly").html(trackData.workshop_goals);
                    $("#workshop_schedule_readonly").html(trackData.workshop_schedule);
                    $("#webinar_info_readonly").html(trackData.webinar_info);
                    // Alusta WYSIWYG-editorit ja aseta arvot
                    self._enableWysiwyg([
                        {
                            selector: 'textarea[name="description"]',
                            content: trackData.description,
                        },
                        {
                            selector: 'textarea[name="target_group_info"]',
                            content: trackData.target_group_info,
                        },
                        {
                            selector: 'textarea[name="extra_info"]',
                            content: trackData.extra_info,
                        },
                        // {
                        //     selector: 'textarea[name="webinar_info"]',
                        //     content: trackData.webinar_info,
                        // },
                        // {selector: 'textarea[name="workshop_goals"]', content: trackData.workshop_goals},
                        // {selector: 'textarea[name="workshop_schedule"]', content: trackData.workshop_schedule},
                    ]);

                    self._renderSpeakers(trackData.speakers);

                    if (trackData.track_confirm) {
                        $("#application-submit-button-send")
                            .attr("name", "track-confirm")
                            .val("track-confirm");
                    }

                    if (
                        isReview &&
                        trackData.can_review &&
                        trackData.rating_grade_ids
                    ) {
                        console.log("===RATING COMMENT===");
                        console.log(trackData.rating_comment);
                        self._enableReviewMode(
                            trackData.rating_grade_ids,
                            trackData.rating,
                            trackData.rating_comment
                        );
                        if (!trackData.show_attachments){
                            $("#existing_attachments").addClass("d-none");
                        }
                    }

                    // Päivitä ja näytä webinar-osio, jos webinar on käytössä
                    self._updateWebinarSection(trackData);

                    // Päivitä ja näytä workshop-osio
                    self._updateWorkshopSection(trackData);

                    if (trackData.is_readonly) {
                        self._makeFieldsReadonly(isReview);
                        self._disableSubmitButtons(isReview);
                        self._disableAddPresenterButton();
                    } else {
                        self._enableSubmitButtons();
                        self._enableAddPresenterButton();
                    }
                });
            }
        });
    },

    _enableReviewMode: function (rating_grade_ids, rating, rating_comment) {
        // Asetetaan lomake tilaan, jossa vain arviointikentät ovat näkyvissä ja muokattavissa
        const reviewDiv = $("#header-track-application-review-div");
        reviewDiv.removeClass("d-none");

        this._populateSelectOptions("rating", rating_grade_ids, rating);

        this._enableWysiwyg([
            {
                selector: 'textarea[name="rating_comment"]',
                content: rating_comment,
            },
        ]);
    },

    _updateWorkshopSection: function (trackData) {
        const workshopDiv = $("#track-application-workshop-div");
        const contractDiv = $("#track-application-workshop-contract-div");
        const workshopRequestDiv = $("#workshop-track-request-time-div");
        if (trackData.is_workshop) {
            workshopDiv.removeClass("d-none");
            this._enableWysiwyg([
                {
                    selector: 'textarea[name="workshop_goals"]',
                    content: trackData.workshop_goals,
                },
                {
                    selector: 'textarea[name="workshop_schedule"]',
                    content: trackData.workshop_schedule,
                },
            ]);
            $('input[name="is_workshop"]').val("true");
            $('input[name="workshop_min_participants"]')
                .val(trackData.workshop_min_participants)
                .prop("disabled", false)
                .attr("required", true);
            $('input[name="workshop_participants"]')
                .val(trackData.workshop_participants)
                .prop("disabled", false)
                .attr("required", true);
            $('input[name="workshop_fee"]')
                .val(trackData.workshop_fee)
                .prop("disabled", false)
                .attr("required", true);
            $('textarea[name="workshop_goals"]')
                .val(trackData.workshop_goals)
                .prop("disabled", false)
                .attr("required", true);
            $('textarea[name="workshop_schedule"]')
                .val(trackData.workshop_schedule)
                .prop("disabled", false)
                .attr("required", true);

            workshopRequestDiv.removeClass("d-none");
            workshopRequestDiv
                .find("select")
                .prop("disabled", false)
                .attr("required", true);
            this._populateSelectOptions(
                "request_time",
                trackData.request_time,
                trackData.req_time
            );

            if (trackData.is_workshop_contract) {
                contractDiv.removeClass("d-none");
                $('input[name="is_workshop_contract"]').val("true");
                $('input[name="signee_firstname"]')
                    .val(trackData.signee_firstname)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="signee_lastname"]')
                    .val(trackData.signee_lastname)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="signee_email"]')
                    .val(trackData.signee_email)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="signee_phone"]')
                    .val(trackData.signee_phone)
                    .prop("disabled", false);
                $('input[name="signee_organization"]')
                    .val(trackData.signee_organization)
                    .prop("disabled", false);
                $('input[name="signee_title"]')
                    .val(trackData.signee_title)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="organizer_organization"]')
                    .val(trackData.organizer_organization)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="organizer_street"]')
                    .val(trackData.organizer_street)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="organizer_zip"]')
                    .val(trackData.organizer_zip)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="organizer_city"]')
                    .val(trackData.organizer_city)
                    .prop("disabled", false)
                    .attr("required", true);
                $('select[name="einvoice_operator_id"]')
                    .val(trackData.einvoice_operator_id)
                    .prop("disabled", false)
                    .attr("required", true);

                this._populateSelectOptions(
                    "einvoice_operator_id",
                    trackData.operators,
                    trackData.einvoice_operator_id
                );
                $('input[name="edicode"]')
                    .val(trackData.edicode)
                    .prop("disabled", false)
                    .attr("required", true);
                $('input[name="organizer_reference"]')
                    .val(trackData.organizer_reference)
                    .prop("disabled", false)
                    .attr("required", true);
            } else {
                contractDiv.addClass("d-none");
                $('input[name="is_workshop_contract"]').val("false");
                contractDiv.find("input, select").prop("disabled", true).val("");
                contractDiv.find("textarea").prop("disabled", true).val("");
            }
        } else {
            workshopDiv.addClass("d-none");
            $('input[name="is_workshop"]').val("false");
            workshopDiv.find("input, select").prop("disabled", true).val("");
            workshopDiv.find("textarea").prop("disabled", true).val("");

            workshopRequestDiv.addClass("d-none");
            workshopRequestDiv
                .find("select")
                .prop("disabled", true)
                .attr("required", false)
                .val("");
        }
    },

    _updateWebinarSection: function (trackData) {
        const webinarDiv = $("#track-application-webinar-div");
        const webinarCheckbox = $('input[name="webinar"]');
        const webinarInfo = $('textarea[name="webinar_info"]');
        const isWebinar = trackData.is_webinar || false;

        if (isWebinar) {
            webinarDiv.removeClass("d-none");
            $('input[name="is_webinar"]').val("true");
            webinarCheckbox.prop("checked", trackData.webinar);
            webinarCheckbox.prop("disabled", false);
            webinarInfo.prop("disabled", !trackData.webinar);
            webinarInfo.val(trackData.webinar_info || "");

            this._enableWysiwyg([
                {
                    selector: 'textarea[name="webinar_info"]',
                    content: trackData.webinar_info,
                },
            ]);
        } else {
            webinarDiv.addClass("d-none");
            $('input[name="is_webinar"]').val("false");
            webinarCheckbox.prop("checked", false);
            webinarCheckbox.prop("disabled", true);
            webinarInfo.prop("disabled", true);
            webinarInfo.val("");
        }
    },

    _populateSelectOptions: function (selectName, options, selectedIds = null) {
        const $select = $(`select[name="${selectName}"]`);
        const isMultiple = $select.attr("multiple") === "multiple";
        $select.empty();

        if (!isMultiple) {
            $select.append('<option value="">Select...</option>');
        }

        options.forEach((option) => {
            const isSelected =
                Array.isArray(selectedIds) && selectedIds.includes(option.id);

            // Rakennetaan option elementti, joka sisältää tarvittavat attribuutit
            const $option = $(`<option></option>`)
                .attr("value", option.id)
                .attr("data-workshop", option.workshop)
                .attr("data-workshop-contract", option.workshop_contract)
                .attr("data-webinar", option.webinar)
                .attr("data-description", option.description || "")
                .text(option.name);

            if (isSelected) {
                $option.attr("selected", "selected");
            }

            $select.append($option);
        });

        if (!Array.isArray(selectedIds) && selectedIds) {
            $select.val(selectedIds);
        }

        if (selectName === "type") {
            this._updateTypeDescription();
        }
    },

    _updateTypeDescription: function () {
        const $typeSelect = $('select[name="type"]');
        const description = $typeSelect.find("option:selected").data("description");
        $("#application_type_description").html(description || ""); // Päivitä kuvauksen kenttä
    },

    _disableAddPresenterButton: function () {
        // Piilota tai disabloi Add Presenter -painike
        $("#add_speaker").attr("disabled", true).hide();
        $("#clear-attachment").attr("disabled", true).hide();
        $(".remove-attachment").attr("disabled", true).hide();
    },

    _enableAddPresenterButton: function () {
        // Näytä ja aktivoi Add Presenter -painike
        $("#add_speaker").attr("disabled", false).show();
    },

    _makeFieldsReadonly: function (isReview) {
        const $form = $(".js_website_submit_cfp_form");
        console.log($form);
        console.log("====LAITETAAN READONLY====");
        if (!isReview) {
            console.log("===KENTÄT READONLY====");
            // Aseta kaikki lomakkeen kentät readonly-tilaan
            $form.find("input, textarea, select").each(function () {
                $(this).attr("readonly", true).attr("disabled", true);
            });

            $form.find(".o_wysiwyg_textarea_wrapper").each(function () {
                // Hide editor, show div with content
                $(this).hide();
                $(".readonly-field").removeClass("d-none");
            });

            // Poista readonly tai disabled attribuutit vain modaalin sulkemispainikkeista
            $form.find(".warning-close-modal").attr("disabled", false);
        } else {
            $form
                .find("input, textarea, select")
                .attr("readonly", true)
                .attr("disabled", true);

            $form.find(".o_wysiwyg_textarea_wrapper").each(function () {
                // Tarkista, onko kenttä 'rating_comment', jos ei ole, piilotetaan editori
                if (!$(this).find('textarea[name="rating_comment"]').length) {
                    $(this).hide();
                }
                $(".readonly-field").removeClass("d-none");
            });
            $form.find("#rating_comment_readonly").addClass("d-none");
            // Jätä seuraavat kentät editoitaviksi
            const editableFields = [
                'textarea[name="rating_comment"]',
                'select[name="rating"]',
            ];
            editableFields.forEach(function (selector) {
                $form.find(selector).removeAttr("readonly").removeAttr("disabled");
            });
        }
    },

    _disableSubmitButtons: function (isReview) {
        if (!isReview) {
            // Piilota tai disabloi painikkeet Save as Draft ja Save and Confirm
            $("#application-submit-button").attr("disabled", true).hide();
            $("#application-submit-button-send").attr("disabled", true).hide();
        } else {
            // Näytä ja aktivoi arvostelun lähetyspainikkeet ja info-osio

            $("#application-submit-button-send").attr("disabled", false).show();
            $("#application-submit-button-send").attr("name", "review-confirm");
            $("#application-submit-button-send").attr("value", "review-confirm");
            $("#application-submit-button-send").attr(
                "title",
                'By clicking "Submit Review" the review of the proposal shall be submitted.'
            );

            $("#application-submit-button").attr("disabled", true).hide();
        }
    },

    _enableSubmitButtons: function () {
        // Näytä ja aktivoi painikkeet Save as Draft ja Save and Confirm
        $("#application-submit-button").attr("disabled", false).show();
        $("#application-submit-button-send").attr("disabled", false).show();
    },

    _clearFormOnClose: function () {
        $("#modal_event_track_application").on("hide.bs.modal", function () {
            // Hae lomakeelementti ja resetoi se
            $("#track-application-form")[0].reset();
        });
    },

    _bindAddSpeaker: function () {
        const container = $(".track-application-speakers-div-container");

        $("#add_speaker").click(function () {
            const lastRow = container.find(
                ".track-application-speakers-div-row-container:last"
            );
            const newRow = lastRow.clone(); // Clone the last row
            const newIndex =
                parseInt($("#track-application-speaker-input-index").val()) + 1;

            newRow.find("input, label").each(function () {
                const elem = $(this);
                const nameAttr = elem.attr("name");
                const forAttr = elem.attr("for");

                if (nameAttr) {
                    elem.attr("name", nameAttr.replace(/\[\d+\]/, `[${newIndex}]`));
                }
                if (forAttr) {
                    elem.attr("for", forAttr.replace(/\[\d+\]/, `[${newIndex}]`));
                }
            });

            newRow.attr("id", newIndex);
            newRow.find(".presenter-span").text(`Presenter #${newIndex}`);
            newRow.find("input").val(""); // Clear values
            newRow.find(".btn-remove-speaker").prop("disabled", false);

            container.append(newRow);
            $("#track-application-speaker-input-index").val(newIndex); // Update the index
        });
    },

    _bindFormSubmit: function () {
        const self = this;

        let activeButton = null; // Muuttuja painetun painikkeen seuraamiseksi

        // Kuuntele painikkeen klikkausta ja tallenna painike aktiiviseksi
        $("#track-application-form").on("click", '[type="submit"]', function () {
            activeButton = $(this); // Tallenna klikatun painikkeen viittaus
        });
        $("#track-application-form").on("submit", function (e) {
            e.preventDefault(); // Estä lomakkeen oletuslähetys

            // Päivitä WYSIWYG-editorin sisältö ennen lomakkeen lähetystä
            const wysiwygGoals = $('textarea[name="workshop_goals"]').data("wysiwyg");
            const wysiwygWebinar = $('textarea[name="webinar_info"]').data("wysiwyg");
            const wysiwygRating = $('textarea[name="rating_comment"]').data("wysiwyg");
            const wysiwygSchedule = $('textarea[name="workshop_schedule"]').data(
                "wysiwyg"
            );

            if (wysiwygGoals) {
                $('textarea[name="workshop_goals"]').val(wysiwygGoals.getValue()); // Aseta WYSIWYG-editorin arvo tekstikenttään
            }

            if (wysiwygRating) {
                $('textarea[name="rating_comment"]').val(wysiwygRating.getValue()); // Aseta WYSIWYG-editorin arvo tekstikenttään
            }

            if (wysiwygSchedule) {
                $('textarea[name="workshop_schedule"]').val(wysiwygSchedule.getValue()); // Aseta WYSIWYG-editorin arvo tekstikenttään
            }
            if (wysiwygWebinar) {
                $('textarea[name="webinar_info"]').val(wysiwygWebinar.getValue()); // Aseta WYSIWYG-editorin arvo tekstikenttään
            }

            const loadingScreen = function () {
                const message = "Loading, please wait...";
                const displayMessage = `
                    <div id="loading-screen" style="
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0, 0, 0, 0.5);
                        z-index: 9999;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #fff;
                        text-align: center;
                        font-size: 20px;
                    ">
                        <div>
                            <img src="/web/static/img/spin.png"
                                style="animation: fa-spin 1s infinite steps(12); width: 50px; height: 50px;"/>
                            <br/><br/>
                            <h4>${message}</h4>
                        </div>
                    </div>`;
                $("body").append(displayMessage);
            };

            const hideLoadingScreen = function () {
                $("#loading-screen").remove();
            };

            loadingScreen(); // Näytä latausruutu

            // TODO TEXTAREA PAKOLLISUUDEN TARKITUS

            const submitButton = $(this).find('[type="submit"]');
            submitButton.prop("disabled", true); // Poista käytöstä lähetyspainike, jotta vältetään kaksoislähetys
            const formData = new FormData(this); // Kerää lomaketiedot
            if (activeButton && activeButton.attr("name") === "review-confirm") {
                const track_id = $('input[name="track_id"]').val();
                formData.append('track_id', track_id);

                const csrfToken = $('input[name="csrf_token"]').val();
                formData.append('csrf_token', csrfToken);
            }

            const action = $(this).attr("action"); // Hae lomakkeen action-osoite

            // Lisää painetun painikkeen arvo lomakedataan, jos painike on asetettu
            if (activeButton && activeButton.attr("name")) {
                formData.append(activeButton.attr("name"), activeButton.val());
            }

            $.ajax({
                url: action,
                type: "POST",
                data: formData,
                processData: false, // Älä käsittele tiedostoja
                contentType: false, // Aseta contentType falseksi, jotta jQuery lähettää lomakkeen tiedot oikein
                success: function (response) {
                    const jsonResponse = JSON.parse(response);
                    if (jsonResponse.success) {
                        // Tyhjennä lomake
                        $("#track-application-form")[0].reset();

                        // Sulje modaali
                        $("#modal_event_track_application").modal("hide");

                        // Näytä onnistumisviesti
                        self._showSuccessMessage(jsonResponse.message);
                    } else if (jsonResponse.error) {
                        console.error("Virhe: " + jsonResponse.error);
                    }
                },
                error: function (error) {
                    console.error("Tapahtui virhe:", error);
                    alert("Odottamaton virhe.");
                },
                complete: function () {
                    hideLoadingScreen(); // Piilota latausruutu
                    submitButton.prop("disabled", false); // Ota lähetyspainike uudelleen käyttöön
                },
            });
        });
    },

    /**
     * Bindaa type-valikon muutokseen tarvittavat tapahtumat
     */
    _bindTypeChange: function () {
        const self = this;
        $(document).ready(function () {
            $("#type").change(function () {
                const selectedType = $("#type option:selected");
                const description = selectedType.attr("data-description") || "";
                $("#application_type_description").html(description);

                const workshop = selectedType.attr("data-workshop");

                const webinar = selectedType.attr("data-webinar");

                self._toggleWorkshopSection(workshop);
                self._toggleWebinarSection(webinar);
            });
        });
    },

    _toggleWorkshopSection: function (workshop, workshopContract) {
        const workshopDiv = $("#track-application-workshop-div");
        const workshopRequestDiv = $("#workshop-track-request-time-div");
        const contractDiv = $("#track-application-workshop-contract-div");

        // Tarkistetaan, että workshop on nimenomaan "true"
        if (workshop === "true") {
            workshopDiv.removeClass("d-none");
            $('input[name="is_workshop"]').val("true");
            workshopDiv
                .find("input, select")
                .prop("disabled", false)
                .attr("required", true);
            workshopDiv.find("textarea").prop("disabled", false).attr("required", true);

            this._enableWysiwyg([
                {selector: 'textarea[name="workshop_goals"]'},
                {selector: 'textarea[name="workshop_schedule"]'},
            ]);

            workshopRequestDiv.removeClass("d-none");
            workshopRequestDiv
                .find("select")
                .prop("disabled", false)
                .attr("required", true);
            // TODO TÄHÄN PAKOLLISET KENTÄT

            if (workshopContract === "true") {
                contractDiv.removeClass("d-none");
                contractDiv.find("input, select").prop("disabled", false);
                contractDiv.find("textarea").prop("disabled", false);
            } else {
                contractDiv.addClass("d-none");
                contractDiv.find("input, select").prop("disabled", true).val("");
                contractDiv.find("textarea").prop("disabled", true).val("");
            }
        } else {
            workshopDiv.addClass("d-none");
            $('input[name="is_workshop"]').val("false");
            workshopDiv
                .find("input, select")
                .prop("disabled", true)
                .val("")
                .attr("required", false);
            workshopDiv
                .find("textarea")
                .prop("disabled", true)
                .val("")
                .attr("required", false);

            workshopRequestDiv.addClass("d-none");
            workshopRequestDiv
                .find("select")
                .prop("disabled", true)
                .val("")
                .attr("required", false);
        }
    },

    _toggleWebinarSection: function (webinar) {
        const webinarDiv = $("#track-application-webinar-div");
        const webinarCheckbox = $('input[name="webinar"]');
        const webinarInfo = $('textarea[name="webinar_info"]');

        if (webinar) {
            // This._enableWysiwyg([
            //     { selector: 'textarea[name="webinar_info"]' },
            // ]);
            webinarDiv.removeClass("d-none");
            $('input[name="is_webinar"]').val("true");
            webinarCheckbox.prop("disabled", false);
            webinarCheckbox.change(function () {
                webinarInfo.prop("disabled", !this.checked);
            });
        } else {
            webinarDiv.addClass("d-none");
            $('input[name="is_webinar"]').val("false");
            webinarCheckbox.prop("disabled", true);
            webinarInfo.prop("disabled", true);
            webinarCheckbox.prop("checked", false);
            webinarInfo.val("");
        }
    },

    _showSuccessMessage: function (message) {
        new Dialog(this, {
            title: _t("Success"),
            size: "medium",
            $content: $("<div/>").html(message), // Lisätään HTML sisältö
            buttons: [
                {
                    text: _t("OK"),
                    close: true,
                    click: function () {
                        // Ladataan sivu uudelleen, kun käyttäjä sulkee ilmoituksen
                        location.reload();
                    },
                },
            ],
        }).open();
    },

    /**
     * Aktivoi WYSIWYG-editori tekstialueille core-mallin mukaisesti
     */
    _enableWysiwyg: function (selectors = []) {
        const self = this;

        if (!Array.isArray(selectors) || selectors.length === 0) {
            console.error("No selectors provided for WYSIWYG initialization.");
            return;
        }

        selectors.forEach((selector) => {
            const $textarea = $(selector.selector);

            if ($textarea.length === 0) {
                console.error(
                    `Textarea element not found for WYSIWYG initialization: ${selector.selector}`
                );
                return;
            }

            // Tarkista, onko WYSIWYG-editori jo alustettu
            if ($textarea.data("wysiwyg")) {
                console.log(
                    `WYSIWYG-editor already initialized for: ${selector.selector}`
                );
                return;
            }

            const options = {
                toolbarTemplate: "website_forum.web_editor_toolbar",
                toolbarOptions: {
                    showColors: false,
                    showFontSize: false,
                    showHistory: true,
                    showHeading1: false,
                    showHeading2: false,
                    showHeading3: false,
                    showLink: true,
                    showImageEdit: true,
                },
                recordInfo: {
                    context: self._getContext(),
                    res_model: "event.track",
                    res_id: Number(
                        window.location.pathname.split("-").slice(-1)[0].split("/")[0]
                    ),
                },
                resizable: true,
                userGeneratedContent: true,
                height: 350,
            };

            loadWysiwygFromTextarea(self, $textarea[0], options).then((wysiwyg) => {
                if (selector.content) {
                    wysiwyg.setValue(selector.content); // Aseta olemassa oleva sisältö editoriin
                }
                $textarea.data("wysiwyg", wysiwyg); // Tallenna viite WYSIWYG-editoriin
            });
        });
    },
});

export default publicWidget.registry.TrackProposalFormInstance;
