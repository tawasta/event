/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadWysiwygFromTextarea } from "@web_editor/js/frontend/loadWysiwygFromTextarea"; // WYSIWYG loader import
import {jsonrpc} from "@web/core/network/rpc_service"; // jsonrpc import
import Dialog from '@web/legacy/js/core/dialog';
import { _t } from "@web/core/l10n/translation";
//import { qweb } from 'web.core';


publicWidget.registry.TrackProposalFormInstance = publicWidget.Widget.extend({
    selector: '#modal_event_track_application',

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
        this._bindFormSubmit();  // Bindataan lomakkeen submit AJAX-pyyntöön
        this._bindAddSpeaker();
        this._removeAttachments();
    },

    _removeAttachments: function () {
        const self = this;

        $("#btn-remove-attachment").click(function () {
            $("#attachment_ids").val("");
        });
    },


    _renderSpeakers: function (speakers) {
        const container = $(".track-application-speakers-div-container");
        const firstRow = container.find(".track-application-speakers-div-row-container:first");

        // Ensimmäinen puhuja asetetaan olemassa oleviin kenttiin
        if (speakers.length > 0) {
            const firstSpeaker = speakers[0];
            firstRow.find(".presenter-span").text(`Presenter #1`);
            firstRow.find("input[name^='speaker_firstname']").val(firstSpeaker.firstname);
            firstRow.find("input[name^='speaker_lastname']").val(firstSpeaker.lastname);
            firstRow.find("input[name^='speaker_email']").val(firstSpeaker.email);
            firstRow.find("input[name^='speaker_phone']").val(firstSpeaker.phone);
            firstRow.find("input[name^='speaker_organization']").val(firstSpeaker.organization);
            firstRow.find("input[name^='speaker_title']").val(firstSpeaker.title);
        }

        let speakerCount = 1;

        // Loput puhujat lisätään kloonaamalla ensimmäinen rivi
        speakers.slice(1).forEach((speaker, index) => {
            speakerCount = index + 2;  // Aloitetaan laskeminen 2:sta

            const newRow = firstRow.clone();
            newRow.attr("id", speakerCount);

            // Päivitetään kenttien arvot
            newRow.find(".presenter-span").text(`Presenter #${speakerCount}`);
            newRow.find("input[name^='speaker_firstname']").val(speaker.firstname);
            newRow.find("input[name^='speaker_lastname']").val(speaker.lastname);
            newRow.find("input[name^='speaker_email']").val(speaker.email);
            newRow.find("input[name^='speaker_phone']").val(speaker.phone);
            newRow.find("input[name^='speaker_organization']").val(speaker.organization);
            newRow.find("input[name^='speaker_title']").val(speaker.title);

            // Päivitetään kenttien id:t ja name-attribuutit oikeiksi
            newRow.find("label[for^='speaker_firstname']").attr("for", `speaker_firstname[${speakerCount}]`);
            newRow.find("input[name^='speaker_firstname']").attr("name", `speaker_firstname[${speakerCount}]`);
            newRow.find("label[for^='speaker_lastname']").attr("for", `speaker_lastname[${speakerCount}]`);
            newRow.find("input[name^='speaker_lastname']").attr("name", `speaker_lastname[${speakerCount}]`);
            newRow.find("label[for^='speaker_email']").attr("for", `speaker_email[${speakerCount}]`);
            newRow.find("input[name^='speaker_email']").attr("name", `speaker_email[${speakerCount}]`);
            newRow.find("label[for^='speaker_phone']").attr("for", `speaker_phone[${speakerCount}]`);
            newRow.find("input[name^='speaker_phone']").attr("name", `speaker_phone[${speakerCount}]`);
            newRow.find("label[for^='speaker_organization']").attr("for", `speaker_organization[${speakerCount}]`);
            newRow.find("input[name^='speaker_organization']").attr("name", `speaker_organization[${speakerCount}]`);
            newRow.find("label[for^='speaker_title']").attr("for", `speaker_title[${speakerCount}]`);
            newRow.find("input[name^='speaker_title']").attr("name", `speaker_title[${speakerCount}]`);

            // Poista "disabled" attribuutti "Remove speaker" -painikkeesta kloonatuilla riveillä
            newRow.find(".btn-remove-speaker").removeAttr("disabled");

            container.append(newRow);
        });

        // Päivitetään piilotettu input, joka seuraa puhujien lukumäärää
        $("#track-application-speaker-input-index").val(speakerCount);
    },





    _loadTrackData: function () {
        const self = this;
        $('#modal_event_track_application').on('show.bs.modal', function (event) {
            console.log("===MENEE TANNE NAIN=====");
            var button = $(event.relatedTarget);
            var trackId = button.data('track-id'); // Get track ID from button
            var eventId = button.data('event-id'); // Hae event ID napista
            console.log(trackId);

            var isReview = button.data('review') || false;  // Tarkistetaan, onko kyseessä arvostelutila
            console.log("==REVIEW===");
            console.log(isReview);


            // Estä modalin näyttäminen ennen kuin data on ladattu ja asetettu
            //event.preventDefault();
            // Piilota modal aluksi
            $('#modal_event_track_application').modal('hide');

            // Määritä action URL ja aseta se lomakkeelle
            var actionUrl = `/event/${eventId}/track_proposal/post`;
            $('#track-application-form').attr('action', actionUrl);

            if (!trackId) {
                // Jos trackId ei ole määritelty, hae eventin track_types_ids
                jsonrpc('/event/application_types', {
                    'event_id': eventId,
                }).then((response) => {
                    self._populateSelectOptions('type', response.application_types);
                    self._populateSelectOptions('target_groups', response.target_groups);
                    self._populateSelectOptions('tags', response.tags);
                    $('#modal_event_track_application').modal('show');
                });
            } else {

                var action = "/event/track/data/" + trackId;
                jsonrpc('/event/track/data', {
                    'track_id': trackId,
                    'isReview': isReview,
                }).then((trackData) => {
                    console.log(trackData);
                    self._populateSelectOptions('type', trackData.application_types, trackData.type);
                    self._populateSelectOptions('target_groups', trackData.target_groups, trackData.target_group_ids);
                    self._populateSelectOptions('tags', trackData.tags, trackData.tag_ids);


                    $('input[name="track_id"]').val(trackData.track_id);
                    $('input[name="name"]').val(trackData.name);
                    $('textarea[name="description"]').val(trackData.description);
                    $('input[name="video_url"]').val(trackData.video_url);
                    $('select[name="language"]').val(trackData.language);
                    $('textarea[name="target_group_info"]').val(trackData.target_group_info);
                    $('textarea[name="extra_info"]').val(trackData.extra_info);

                    $('input[name="contact_firstname"]').val(trackData.contact.firstname);
                    $('input[name="contact_lastname"]').val(trackData.contact.lastname);
                    $('input[name="contact_email"]').val(trackData.contact.email);
                    $('input[name="contact_phone"]').val(trackData.contact.phone);
                    $('input[name="contact_organization"]').val(trackData.contact.organization);
                    $('input[name="contact_title"]').val(trackData.contact.title);


                    self._renderSpeakers(trackData.speakers);

                    if (isReview && trackData.can_review && trackData.rating_grade_ids) {
                        self._enableReviewMode(trackData.rating_grade_ids);  
                    }

                    if (trackData.is_readonly) {
                        self._makeFieldsReadonly(isReview);
                        self._disableSubmitButtons(isReview);  // Disable the save buttons if readonly
                        self._disableAddPresenterButton();
                    } else {
                        self._enableSubmitButtons();  // Enable the save buttons if not readonly
                        self._enableAddPresenterButton();
                    }

                    // Päivitä ja näytä webinar-osio, jos webinar on käytössä
                    self._updateWebinarSection(trackData);

                    // Päivitä ja näytä workshop-osio
                    self._updateWorkshopSection(trackData);

                    // Nyt kun lomakkeen tiedot on asetettu, näytetään modal
                    $('#modal_event_track_application').modal('show');
                });
            }


        });
    },

    _enableReviewMode: function(rating_grade_ids) {
        // Asetetaan lomake tilaan, jossa vain arviointikentät ovat näkyvissä ja muokattavissa
        console.log("==LUPA ARVIOIDA====");
        const reviewDiv = $('#header-track-application-review-div');
        reviewDiv.removeClass('d-none');

        this._populateSelectOptions('rating', rating_grade_ids);
    },

    _updateWorkshopSection: function(trackData) {
        const workshopDiv = $('#track-application-workshop-div');
        const contractDiv = $('#track-application-workshop-contract-div');
        console.log(trackData.type);
        console.log(trackData.type.workshop);
        if (trackData.is_workshop) {
            console.log("===ON WORKSHOPPI===");
            workshopDiv.removeClass('d-none');
            $('input[name="is_workshop"]').val('true');
            $('input[name="workshop_min_participants"]').val(trackData.workshop_min_participants).prop('disabled', false).attr('required', true);
            $('input[name="workshop_participants"]').val(trackData.workshop_participants).prop('disabled', false).attr('required', true);
            $('input[name="workshop_fee"]').val(trackData.workshop_fee).prop('disabled', false).attr('required', true);
            $('textarea[name="workshop_goals"]').val(trackData.workshop_goals).prop('disabled', false).attr('required', true);
            $('textarea[name="workshop_schedule"]').val(trackData.workshop_schedule).prop('disabled', false).attr('required', true);

            if (trackData.is_workshop_contract) {
                contractDiv.removeClass('d-none');
                $('input[name="is_workshop_contract"]').val('true');
                $('input[name="signee_firstname"]').val(trackData.signee_firstname).prop('disabled', false).attr('required', true);
                $('input[name="signee_lastname"]').val(trackData.signee_lastname).prop('disabled', false).attr('required', true);
                $('input[name="signee_email"]').val(trackData.signee_email).prop('disabled', false).attr('required', true);
                $('input[name="signee_phone"]').val(trackData.signee_phone).prop('disabled', false);
                $('input[name="signee_organization"]').val(trackData.signee_organization).prop('disabled', false);
                $('input[name="signee_title"]').val(trackData.signee_title).prop('disabled', false).attr('required', true);
                $('input[name="organizer_organization"]').val(trackData.organizer_organization).prop('disabled', false).attr('required', true);
                $('input[name="organizer_street"]').val(trackData.organizer_street).prop('disabled', false).attr('required', true);
                $('input[name="organizer_zip"]').val(trackData.organizer_zip).prop('disabled', false).attr('required', true);
                $('input[name="organizer_city"]').val(trackData.organizer_city).prop('disabled', false).attr('required', true);
                $('select[name="einvoice_operator_id"]').val(trackData.einvoice_operator_id).prop('disabled', false).attr('required', true);
                $('input[name="edicode"]').val(trackData.edicode).prop('disabled', false).attr('required', true);
                $('input[name="organizer_reference"]').val(trackData.organizer_reference).prop('disabled', false).attr('required', true);
            } else {
                contractDiv.addClass('d-none');
                $('input[name="is_workshop_contract"]').val('false');
                contractDiv.find('input, select').prop('disabled', true).val('');
                contractDiv.find('textarea').prop('disabled', true).val('');
            }
        } else {
            workshopDiv.addClass('d-none');
            $('input[name="is_workshop"]').val('false');
            workshopDiv.find('input, select').prop('disabled', true).val('');
            workshopDiv.find('textarea').prop('disabled', true).val('');
        }
    },


    _updateWebinarSection: function(trackData) {
        const webinarDiv = $('#track-application-webinar-div');
        const webinarCheckbox = $('input[name="webinar"]');
        const webinarInfo = $('textarea[name="webinar_info"]');
        const isWebinar = trackData.type.webinar || false;

        if (isWebinar) {
            webinarDiv.removeClass('d-none');
            $('input[name="is_webinar"]').val('true');
            webinarCheckbox.prop('checked', trackData.webinar);
            webinarCheckbox.prop('disabled', false);
            webinarInfo.prop('disabled', !trackData.webinar);
            webinarInfo.val(trackData.webinar_info || '');
        } else {
            webinarDiv.addClass('d-none');
            $('input[name="is_webinar"]').val('false');
            webinarCheckbox.prop('checked', false);
            webinarCheckbox.prop('disabled', true);
            webinarInfo.prop('disabled', true);
            webinarInfo.val('');
        }
    },


    _populateSelectOptions: function(selectName, options, selectedIds = null) {
        const $select = $(`select[name="${selectName}"]`);
        $select.empty();

        $select.append('<option value="">Select...</option>');

        options.forEach((option) => {
            const isSelected = Array.isArray(selectedIds) && selectedIds.includes(option.id);
            
            // Rakennetaan option elementti, joka sisältää tarvittavat attribuutit
            const $option = $(`<option></option>`)
                .attr('value', option.id)
                .attr('data-workshop', option.workshop)
                .attr('data-workshop-contract', option.workshop_contract)
                .attr('data-webinar', option.webinar)
                .attr('data-description', option.description || '')
                .text(option.name);

            if (isSelected) {
                $option.attr('selected', 'selected');
            }

            $select.append($option);
        });

        if (!Array.isArray(selectedIds) && selectedIds) {
            $select.val(selectedIds);
        }

        if (selectName === 'type') {
            this._updateTypeDescription();
        }
    },


    _updateTypeDescription: function() {
        const $typeSelect = $('select[name="type"]');
        const description = $typeSelect.find('option:selected').data('description');
        $('#application_type_description').text(description || ''); // Päivitä kuvauksen kenttä
    },

    _disableAddPresenterButton: function() {
        // Piilota tai disabloi Add Presenter -painike
        $('#add_speaker').attr('disabled', true).hide();
    },

    _enableAddPresenterButton: function() {
        // Näytä ja aktivoi Add Presenter -painike
        $('#add_speaker').attr('disabled', false).show();
    },

    _makeFieldsReadonly: function(isReview) {
        console.log("=====DISABLOIDAAN==");
        const $form = $('.js_website_submit_cfp_form');
        if (!isReview) {
            console.log("kentat readonly ja disabled");
            console.log($form);
            // Aseta kaikki lomakkeen kentät readonly-tilaan
            $form.find('input, textarea, select').attr('readonly', true).attr('disabled', true);

            // Poista readonly tai disabled attribuutit vain modaalin sulkemispainikkeista
            $form.find('.warning-close-modal').attr('disabled', false);
        } else {
            $form.find('input, textarea, select').attr('readonly', true).attr('disabled', true);
            // Jätä seuraavat kentät editoitaviksi
            const editableFields = [
                'textarea[name="rating_comment"]',
                'select[name="rating"]',
            ];
            console.log("naytetaan arviointi kentät");
            editableFields.forEach(function(selector) {
                $form.find(selector).removeAttr('readonly').removeAttr('disabled');
            });

        }
        
    },

    _disableSubmitButtons: function(isReview) {

        if (!isReview) {
            // Piilota tai disabloi painikkeet Save as Draft ja Save and Confirm
            $('#application-submit-button').attr('disabled', true).hide();
            $('#application-submit-button-send').attr('disabled', true).hide();
        } else {
            console.log("NÄYTETÄÄN ARVIOINTI PAINIKKEET");
            // Näytä ja aktivoi arvostelun lähetyspainikkeet ja info-osio
            
            $('#application-submit-button-send').attr('disabled', false).show();
            $('#application-submit-button-send').attr('name', 'review-confirm');
            $('#application-submit-button-send').attr('value', 'review-confirm');
            $('#application-submit-button-send').attr('title', 'By clicking "Submit Review" the review of the proposal shall be submitted.');

            $('#application-submit-button').attr('disabled', true).hide();
        }
    },

    _enableSubmitButtons: function() {

        // Näytä ja aktivoi painikkeet Save as Draft ja Save and Confirm
        $('#application-submit-button').attr('disabled', false).show();
        $('#application-submit-button-send').attr('disabled', false).show();
    },

    _clearFormOnClose: function () {
        $('#modal_event_track_application').on('hide.bs.modal', function () {
            // Hae lomakeelementti ja resetoi se
            $('#track-application-form')[0].reset();
        });
    },

    _bindAddSpeaker: function () {
        const self = this;
        const container = $(".track-application-speakers-div-container");

        $("#add_speaker").click(function () {
            const lastRow = container.find(".track-application-speakers-div-row-container:last");
            const newRow = lastRow.clone();  // Clone the last row
            const newIndex = parseInt($("#track-application-speaker-input-index").val()) + 1;

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
            newRow.find("input").val("");  // Clear values

            container.append(newRow);
            $("#track-application-speaker-input-index").val(newIndex);  // Update the index
        });
    },

    _bindFormSubmit: function () {
        const self = this;
        $('#track-application-form').on('submit', function (e) {
            e.preventDefault();  // Estä lomakkeen oletuslähetys

            const submitButton = $(this).find('[type="submit"]');
            submitButton.prop('disabled', true);  // Poista käytöstä lähetyspainike, jotta vältetään kaksoislähetys

            const formData = new FormData(this); // Kerää lomaketiedot
            const action = $(this).attr('action'); // Hae lomakkeen action-osoite

            // Lisää painetun painikkeen arvo lomakedataan
            const activeButton = $(document.activeElement);
            if (activeButton.attr("name")) {
                formData.append(activeButton.attr("name"), activeButton.val());
            }

            $.ajax({
                url: action,
                type: 'POST',
                data: formData,
                processData: false, // Älä käsittele tiedostoja
                contentType: false, // Aseta contentType falseksi, jotta jQuery lähettää lomakkeen tiedot oikein
                success: function (response) {
                    const jsonResponse = JSON.parse(response);
                    if (jsonResponse.success) {
                        console.log("Lomake lähetettiin onnistuneesti");

                        // Tyhjennä lomake
                        $('#track-application-form')[0].reset();

                        // Sulje modaali
                        $('#modal_event_track_application').modal('hide');

                        // Näytä onnistumisviesti
                        self._showSuccessMessage(jsonResponse.message);
                    } else if (jsonResponse.error) {
                        console.error("Virhe: " + jsonResponse.error);
                    }
                },
                error: function (error) {
                    console.error("Tapahtui virhe:", error);
                    alert('Odottamaton virhe.');
                },
                complete: function () {
                    submitButton.prop('disabled', false);  // Ota lähetyspainike uudelleen käyttöön
                }
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
                console.log("===VAIHTUUU====");
                const selectedType = $("#type option:selected");
                const description = selectedType.attr("data-description") || "";
                $("#application_type_description").text(description);

                const workshop = selectedType.attr("data-workshop");
                console.log(workshop);
                const workshopContract = selectedType.attr("data-workshop-contract");
                const webinar = selectedType.attr("data-webinar");

                self._toggleWorkshopSection(workshop);
                self._toggleWebinarSection(webinar);
            });
        });
    },

    _toggleWorkshopSection: function (workshop, workshopContract) {
        const workshopDiv = $('#track-application-workshop-div');
        const contractDiv = $('#track-application-workshop-contract-div');
        
        // Tarkistetaan, että workshop on nimenomaan "true"
        if (workshop === "true") {
            workshopDiv.removeClass('d-none');
            workshopDiv.find('input, select').prop('disabled', false).attr('required', true);
            workshopDiv.find('textarea').prop('disabled', false).attr('required', true);
            // TODO TÄHÄN PAKOLLISET KENTÄT

            if (workshopContract === "true") {
                contractDiv.removeClass('d-none');
                contractDiv.find('input, select').prop('disabled', false);
                contractDiv.find('textarea').prop('disabled', false);
            } else {
                contractDiv.addClass('d-none');
                contractDiv.find('input, select').prop('disabled', true).val('');
                contractDiv.find('textarea').prop('disabled', true).val('');
            }
        } else {
            workshopDiv.addClass('d-none');
            workshopDiv.find('input, select').prop('disabled', true).val('').attr('required', false);
            workshopDiv.find('textarea').prop('disabled', true).val('').attr('required', false);
        }
    },


    _toggleWebinarSection: function (webinar) {
        const webinarDiv = $('#track-application-webinar-div');
        const webinarCheckbox = $('input[name="webinar"]');
        const webinarInfo = $('textarea[name="webinar_info"]');

        if (webinar) {
            webinarDiv.removeClass('d-none');
            webinarCheckbox.prop('disabled', false);
            webinarCheckbox.change(function () {
                webinarInfo.prop('disabled', !this.checked);
            });
        } else {
            webinarDiv.addClass('d-none');
            webinarCheckbox.prop('disabled', true);
            webinarInfo.prop('disabled', true);
            webinarCheckbox.prop('checked', false);
            webinarInfo.val('');
        }
    },

    _showSuccessMessage: function (message) {
        var self = this;
        Dialog.alert(this, message, {
            title: _t("Success"),
            size: 'medium',
            confirm_callback: function () {
                // Tarkistetaan, ollaanko '/proposal' näkymässä
                if (window.location.pathname.includes('/track_proposal')) {
                    $(".proposals").load(
                        window.location.pathname + " .proposals > *",
                        function () {
                            console.log("Proposal view content updated successfully.");
                        }
                    );
                } 
                // Tarkistetaan, ollaanko '/my/tracks' näkymässä
                else if (window.location.pathname.includes('/my/tracks')) {
                    $(".table-responsive").load(
                        window.location.pathname + " .table-responsive > *",
                        function () {
                            console.log("My Tracks view content updated successfully.");
                        }
                    );
                } 
                else {
                    console.log("No specific view update logic for the current path.");
                }
            }
        });
    },

    /**
     * Aktivoi WYSIWYG-editori tekstialueille core-mallin mukaisesti
     */
    _enableWysiwyg: function () {
        const self = this;

        // Käytetään WYSIWYG editoria kaikille o_wysiwyg_loader -tekstikentille
        $('textarea.o_wysiwyg_loader').toArray().forEach((textarea) => {
            var $textarea = $(textarea);
            var $form = $textarea.closest('form');
            var options = {
                toolbarTemplate: 'website_forum.web_editor_toolbar',
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
                    res_model: 'event.track',
                    res_id: +window.location.pathname.split('-').slice(-1)[0].split('/')[0],
                },
                resizable: true,
                userGeneratedContent: true,
                height: 350,
            };

            // Aktivoi WYSIWYG-editori
            loadWysiwygFromTextarea(self, $textarea[0], options).then((wysiwyg) => {
                // Poistetaan float-start-luokka kuvista, jotka sotkevat layoutin
                $form.find('.note-editable').find('img.float-start').removeClass('float-start');
                $form.on('submit', function() {
                    $textarea.val(wysiwyg.getValue());
                });
            });
        });
    }
});

export default publicWidget.registry.TrackProposalFormInstance;
