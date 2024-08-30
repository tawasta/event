/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadWysiwygFromTextarea } from "@web_editor/js/frontend/loadWysiwygFromTextarea"; // WYSIWYG loader import
import {jsonrpc} from "@web/core/network/rpc_service"; // jsonrpc import
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
            console.log(trackId);
            if (!trackId) {
                return;
            }

            // Estä modalin näyttäminen ennen kuin data on ladattu ja asetettu
            //event.preventDefault();
            // Piilota modal aluksi
            $('#modal_event_track_application').modal('hide');

            var action = "/event/track/data/" + trackId;
            jsonrpc('/event/track/data', {
                'track_id': trackId,
            }).then((trackData) => {
                console.log(trackData);
                $('input[name="track_id"]').val(trackData.track_id);
                $('select[name="type"]').val(trackData.type);
                $('input[name="name"]').val(trackData.name);
                $('textarea[name="description"]').val(trackData.description);
                $('input[name="video_url"]').val(trackData.video_url);
                $('select[name="language"]').val(trackData.language);
                $('select[name="target_groups"]').val(trackData.target_group_ids);
                $('textarea[name="target_group_info"]').val(trackData.target_group_info);
                $('textarea[name="extra_info"]').val(trackData.extra_info);

                $('input[name="contact_firstname"]').val(trackData.contact.firstname);
                $('input[name="contact_lastname"]').val(trackData.contact.lastname);
                $('input[name="contact_email"]').val(trackData.contact.email);
                $('input[name="contact_phone"]').val(trackData.contact.phone);
                $('input[name="contact_organization"]').val(trackData.contact.organization);
                $('input[name="contact_title"]').val(trackData.contact.title);

                self._renderSpeakers(trackData.speakers);

                // Nyt kun lomakkeen tiedot on asetettu, näytetään modal
                $('#modal_event_track_application').modal('show');
            });


        });
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
            e.preventDefault();  // Prevent default form submission

            const formData = new FormData(this); // Collect form data
            const action = $(this).attr('action'); // Get the form action

            $.ajax({
                url: action,
                type: 'POST',
                data: formData,
                processData: false, // Don't process the files
                contentType: false, // Set contentType to false as jQuery will tell the server its a query string request
                success: function (response) {
                    const jsonResponse = JSON.parse(response);
                    if (jsonResponse.success) {
                        console.log("Form submitted successfully");

                        // Tyhjennetään lomake
                        $('#track-application-form')[0].reset();

                        // Suljetaan modal
                        $('#modal_event_track_application').modal('hide');

                        // Näytetään onnistumisviesti SweetAlertin avulla
                        self._showSuccessMessage(jsonResponse.message);
                        // Optionally, show success message or redirect
                    } else if (jsonResponse.error) {
                        console.error("Error: " + jsonResponse.error);
                        // Optionally, show error message
                    }
                },
                error: function (error) {
                    console.error("An error occurred:", error);
                    alert('An unexpected error occurred.');
                }
            });
        });
    },


    /**
     * Bindaa type-valikon muutokseen tarvittavat tapahtumat
     */
    _bindTypeChange: function () {
        $(document).ready(function () {
            $("#type").change(function () {
                $("#application_type_description").text(
                            $("#type option:selected").attr("data-description") || ""
                        );
                        var workshop = $("#type option:selected").attr("data-workshop");
                        var workshop_contract = $("#type option:selected").attr(
                            "data-workshop-contract"
                        );
                        var webinar = $("#type option:selected").attr("data-webinar");
                        // Enable workshop inputs
                        if (workshop) {
                            const targetDiv = document.getElementById(
                                "workshop-track-request-time-div"
                            );
                            if (targetDiv) {
                                targetDiv.classList.remove("d-none");
                            }
                            $("#track-application-workshop-div").removeClass("d-none");
                            $("#track-application-workshop-row-div")
                                .find("input#is_workshop")
                                .each(function () {
                                    $(this).attr("value", "true");
                                });
                            $("#track-application-workshop-row-div")
                                .find("input[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("input[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-row-div")
                                .find("select[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("select[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-row-div")
                                .find("textarea[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            $("#track-application-workshop-row-div")
                                .find("textarea[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            // Disable workshop inputs
                        } else {
                            $("#track-application-workshop-div").addClass("d-none");
                            const targetDiv = document.getElementById(
                                "workshop-track-request-time-div"
                            );
                            if (targetDiv) {
                                targetDiv.classList.add("d-none");
                            }
                            $("#track-application-workshop-row-div")
                                .find("input#is_workshop")
                                .each(function () {
                                    $(this).attr("value", "false");
                                });
                            $("#track-application-workshop-row-div")
                                .find("input")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("input[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("select")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("select[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-row-div")
                                .find("textarea")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                            $("#track-application-workshop-row-div")
                                .find("textarea[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                        }
                        // Enable workshop contract inputs
                        if (workshop_contract) {
                            $("#track-application-workshop-contract-div").removeClass(
                                "d-none"
                            );
                            $("#track-application-workshop-contract-div")
                                .find("input#is_workshop_contract")
                                .each(function () {
                                    $(this).attr("value", "true");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("input[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("input[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("select[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("select[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("textarea[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("textarea[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            // Disable workshop contract inputs
                        } else {
                            $("#track-application-workshop-contract-div").addClass(
                                "d-none"
                            );
                            $("#track-application-workshop-contract-div")
                                .find("input#is_workshop_contract")
                                .each(function () {
                                    $(this).attr("value", "false");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("input")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("input[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("input[required]")
                                .each(function () {
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("input[name^='signee']").attr("required", false);
                            $("#track-application-workshop-contract-div")
                                .find("select")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("select[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("textarea")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                            $("#track-application-workshop-contract-div")
                                .find("textarea[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                        }
                        // Display webinar questions depending on type
                        if (webinar) {
                            $("#track-application-webinar-div").removeClass("d-none");
                            $("#track-application-webinar-div")
                                .find("input#is_webinar")
                                .each(function () {
                                    $(this).attr("value", "true");
                                });
                            $("#track-application-webinar-div")
                                .find("input[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-webinar-div")
                                .find("textarea[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            // Disable webinar inputs
                        } else {
                            $("#track-application-webinar-div").addClass("d-none");
                            $("#track-application-webinar-div")
                                .find("input#is_webinar")
                                .each(function () {
                                    $(this).attr("value", "false");
                                });
                            $("#track-application-webinar-div")
                                .find("input")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-webinar-div")
                                .find("textarea")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                        }
            });
        });
    },

    _showSuccessMessage: function (message) {
        console.log("====ONNISTUI====");
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
