$(".toggle-rules").on("click", function () {
    const overlay = $("#overlay");
    const rules = $(".rules-hidden");
    if (overlay.is(":visible")) {
        rules.fadeToggle(500);
        overlay.delay(500).fadeToggle(500);
    } else {
        overlay.fadeToggle(500);
        rules.delay(600).fadeToggle(500);
    }
});
$(function () {
    const main = $("#main");
    $("#dropped").css("height", main.height());
    $("#dropped div").css("height", main.height());
    Dropzone.options.myAwesomeDropzone = {
        url: "/api/upload/file",
        autoProcessQueue: false,
        uploadMultiple: false,
        previewsContainer: "#previews",
        parallelUploads: 2,
        maxFiles: 1000,
        maxFilesize: 1024,
        paramName: "files",
        clickable: "#filess",
        addRemoveLinks: true,
        init: function () {
            const myDropzone = this;
            this.element
                .querySelector('input[name="submit"]')
                .addEventListener("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    myDropzone.processQueue();
                });
            this.on("sending", function (file, xhr, formData) {
            });
            this.on("success", function (file, response) {
                $(".dz-error-message span", file.previewElement).html(
                    '<a href="' + response.full_url + '">' + response.full_url + "</a>"
                );
                $(".dz-error-message", file.previewElement).css("opacity", 1);
                $(".dz-error-mark", file.previewElement).hide();
                myDropzone.processQueue();
            });
            this.on("error", function (file, response) {
                $(".dz-error-message", file.previewElement).css("opacity", 1);
                myDropzone.processQueue();
                file.status = Dropzone.ADDED;
                myDropzone.enqueueFile(file);
            });
        }
    }
});
