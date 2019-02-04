$(".toggle-rules").on("click", function() {
  if ($("#overlay").is(":visible")) {
    $(".rules-hidden").fadeToggle(500);
    $("#overlay")
      .delay(500)
      .fadeToggle(500);
  } else {
    $("#overlay").fadeToggle(500);
    $(".rules-hidden")
      .delay(600)
      .fadeToggle(500);
  }
});
$("#clear-fields").on("click", function() {
  $("#key")
    .get(0)
    .setAttribute("value", "");
  $("#password")
    .get(0)
    .setAttribute("value", "");
});
$(document).ready(function() {
  $("#wrapper").equalHeight();
});
$(function() {
  $("#dropped").css("height", $("#main").height());
  $("#dropped div").css("height", $("#main").height());
  $("#my-awesome-dropzone").dropzone({
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
    init: function() {
      var myDropzone = this;
      this.element
        .querySelector('input[name="submit"]')
        .addEventListener("click", function(e) {
          e.preventDefault();
          e.stopPropagation();
          myDropzone.processQueue();
        });
      this.on("sending", function(file, xhr, formData) {});
      this.on("success", function(file, response) {
        console.log(response);
        console.log(file);
        console.log(file.previewTemplate);
        $(".dz-error-message span", file.previewTemplate).html(
          '<a href="' +
            response.url +
            '">' +
            response.base +
            response.url +
            "</a>"
        );
        $(".dz-error-message", file.previewTemplate).css("opacity", 1);
        myDropzone.processQueue();
      });
      this.on("error", function(file, response) {
        console.log("error:");
        console.log(file);
        console.log(response);
        $(".dz-error-message", file.previewTemplate).css("opacity", 1);
        myDropzone.processQueue();
      });
    }
  });
});
