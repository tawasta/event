odoo.define("survey.survey_page_statistics_inner", function () {
    "use strict";

    $(function () {
        $("#select_event").select2({
            placeholder: "Select events",
            allowClear: true,
        });

        $("#select_event").on("change", function () {
            $("#hidden_events").val($("#select_event").val().toString());
            var path = window.location.pathname;
            var val = $("#hidden_events").val();
            if (path.indexOf("/event") >= 0) {
                path = window.location.pathname.split("/event")[0];
            }

            if (val) {
                window.location.href = path + "/event/" + val;
            } else {
                window.location.href = path;
            }
        });

        $("#select_tag").select2({
            placeholder: "Select tags",
            allowClear: true,
        });

        $("#select_tag").on("change", function () {
            $("#hidden_tags").val($("#select_tag").val().toString());
            var path = window.location.pathname;
            var val = $("#hidden_tags").val();
            if (path.indexOf("/tag") >= 0) {
                path = window.location.pathname.split("/tag")[0];
            }

            if (val) {
                window.location.href = path + "/tag/" + val;
            } else {
                window.location.href = path;
            }
        });

        var path = window.location.pathname;
        if (path.indexOf("/date_start") >= 0) {
            var date_current = path.split("/date_start/")[1];
            var newDateTime = moment(date_current, "DD.MM.YYYY").toDate();
            $("#datetimepicker-filter-date").datetimepicker({
                format: "DD.MM.Y",
                locale: moment.locale(),
                defaultDate: newDateTime,
            });
        } else {
            $("#datetimepicker-filter-date").datetimepicker({
                format: "DD.MM.Y",
                locale: moment.locale(),
            });
        }

        $("#datetimepicker-filter-date").on("hide.datetimepicker", function () {
            var newStartDate = $(this).find(".datetimepicker-input").val();
            var basePath = window.location.pathname
                .split("/date_start")[0]
                .split("/date_end")[0];
            var endDatePath =
                basePath +
                (window.location.pathname.indexOf("/date_end") >= 0
                    ? window.location.pathname.split("/date_end")[1]
                    : "");

            if (newStartDate) {
                var newPath = basePath + "/date_start/" + newStartDate;
                // Check if end_date exists and compare dates
                if (endDatePath) {
                    // Console.log("=====TANNE MENENEE=====");
                    var endDate = moment(
                        window.location.pathname.split("/date_end/")[1],
                        "DD.MM.YYYY"
                    );
                    var startDate = moment(newStartDate, "DD.MM.YYYY");

                    // Console.log(startDate);
                    // console.log(endDate);
                    if (startDate.isBefore(endDate)) {
                        newPath +=
                            "/date_end/" +
                            window.location.pathname.split("/date_end/")[1];
                    }
                }
                window.location.href = newPath;
                // Console.log(newPath);
            } else {
                window.location.href = basePath;
                // Console.log("basePath");
            }
        });

        // Var path = window.location.pathname;
        // if (path.indexOf("/date_start") >= 0) {
        //     var date_current = path.split("/date_start/")[1];
        //     var newDateTime = moment(date_current, "DD.MM.YYYY").toDate();
        //     $("#datetimepicker-filter-date").datetimepicker({
        //         format: "DD.MM.Y",
        //         locale: moment.locale(),
        //         defaultDate: newDateTime,
        //     });
        // } else {
        //     var dateNow = new Date();
        //     $("#datetimepicker-filter-date").datetimepicker({
        //         format: "DD.MM.Y",
        //         locale: moment.locale(),
        //         defaultDate: dateNow,
        //     });
        // }

        // $("#datetimepicker-filter-date").on("change.datetimepicker", function () {
        //     var date = $(this).find(".datetimepicker-input").val();
        //     var path = window.location.pathname;
        //     if (path.indexOf("/date_start") >= 0) {
        //         path = window.location.pathname.split("/date_start")[0];
        //     }

        //     if (date) {
        //         window.location.href = path + "/date_start/" + date;
        //     } else {
        //         window.location.href = path;
        //     }
        // });
        // if (path.indexOf("/date_end") >= 0) {
        //     var date_current = path.split("/date_end/")[1];
        //     var newDateTime = moment(date_current, "DD.MM.YYYY").toDate();
        //     $("#datetimepicker-filter-end-date").datetimepicker({
        //         format: "DD.MM.Y",
        //         locale: moment.locale(),
        //         defaultDate: newDateTime,
        //     });
        // } else {
        //     var dateNow = new Date();
        //     $("#datetimepicker-filter-end-date").datetimepicker({
        //         format: "DD.MM.Y",
        //         locale: moment.locale(),
        //         defaultDate: dateNow,
        //     });
        // }

        // $("#datetimepicker-filter-end-date").on("change.datetimepicker", function () {
        //     var date = $(this).find(".datetimepicker-input").val();
        //     var path = window.location.pathname;
        //     if (path.indexOf("/date_end") >= 0) {
        //         path = window.location.pathname.split("/date_end")[0];
        //     }

        //     if (date) {
        //         window.location.href = path + "/date_end/" + date;
        //     } else {
        //         window.location.href = path;
        //     }
        // });
        if (path.indexOf("/date_end") >= 0) {
            var date_current = path.split("/date_end/")[1];
            var newDateTime = moment(date_current, "DD.MM.YYYY").toDate();
            $("#datetimepicker-filter-end-date").datetimepicker({
                format: "DD.MM.Y",
                locale: moment.locale(),
                defaultDate: newDateTime,
            });
        } else {
            $("#datetimepicker-filter-end-date").datetimepicker({
                format: "DD.MM.Y",
                locale: moment.locale(),
            });
        }

        $("#datetimepicker-filter-end-date").on("hide.datetimepicker", function () {
            var date = $(this).find(".datetimepicker-input").val();
            var path = window.location.pathname;
            if (path.indexOf("/date_end") >= 0) {
                path = window.location.pathname.split("/date_end")[0];
            }

            if (date) {
                window.location.href = path + "/date_end/" + date;
            } else {
                window.location.href = path;
            }
        });
    });
});
