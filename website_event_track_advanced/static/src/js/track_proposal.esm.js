/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadWysiwygFromTextarea } from "@web_editor/js/frontend/loadWysiwygFromTextarea"; // WYSIWYG loader import

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
    },

    _loadTrackData: function () {
        const self = this;
        $('#modal_event_track_application').on('show.bs.modal', function (event) {
            console.log("===MENEE TANNE NAIN=====");
            var button = $(event.relatedTarget);
            var trackId = button.data('track-id'); // Get track ID from button
            console.log(trackId);

            if (trackId) {
                // Use the rpc service to send a request to the server
                this._rpc({
                    route: '/event/track/data',  // Route that processes the request
                    params: {
                        track_id: trackId,
                    },
                }).then(function (data) {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }
                    
                    // Populate the form fields with the track data
                    $('input[name="name"]').val(data.name);
                    $('textarea[name="description"]').val(data.description);
                    $('input[name="video_url"]').val(data.video_url);
                    $('select[name="language"]').val(data.language);
                    $('select[name="target_groups"]').val(data.target_group_ids);
                    $('input[name="contact_firstname"]').val(data.partner_id[1]);

                    // Handle workshop and webinar specific fields
                    if (data.type === 'workshop') {
                        $('#track-application-workshop-div').removeClass('d-none');
                        $('input[name="workshop_participants"]').val(data.workshop_participants);
                        $('input[name="workshop_min_participants"]').val(data.workshop_min_participants);
                        $('input[name="workshop_fee"]').val(data.workshop_fee);
                    } else {
                        $('#track-application-workshop-div').addClass('d-none');
                    }

                    if (data.webinar) {
                        $('#track-application-webinar-div').removeClass('d-none');
                        $('input[name="webinar"]').prop('checked', data.webinar);
                        $('textarea[name="webinar_info"]').val(data.webinar_info);
                    } else {
                        $('#track-application-webinar-div').addClass('d-none');
                    }
                });
            }
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
            });
        });
    }
});

export default publicWidget.registry.TrackProposalFormInstance;
