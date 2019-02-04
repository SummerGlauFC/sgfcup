$.fn.equalHeight = function() {
  var max = 0;
  return this.children()
    .each(function() {
      var height = $(this).height();
      max = height > max ? height : max;
    })
    .height(max);
};
$(window).resize(function() {
  $("#wrapper").equalHeight();
});
$(document).ready(function() {
  $("#wrapper").equalHeight();
});
$("#clear-fields").on("click", function() {
  $("#key")
    .get(0)
    .setAttribute("value", "");
  $("#password")
    .get(0)
    .setAttribute("value", "");
});

$("form").submit(function() {
  var url = "/api/upload/paste";
  $("textarea").hide();
  $.ajax({
    type: "POST",
    url: url,
    data: $("form").serialize(),
    success: function(data) {
      if (data.success) {
        $("#message").html(
          '<a href="' + data.url + '">' + data.base + data.url + "</a>"
        );
      } else {
        $("#message").html(data.error);
      }
      $("#message").fadeIn(250);
    }
  });
  return false;
});
