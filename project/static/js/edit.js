$("#clear-fields").on("click", function() {
  $("#key")
    .get(0)
    .setAttribute("value", "");
  $("#password")
    .get(0)
    .setAttribute("value", "");
});
$("form").submit(function() {
  var url = "/api/edit/paste";
  $("textarea").hide();
  $.ajax({
    type: "POST",
    url: url,
    data: $("form").serialize(),
    success: function(data) {
      // data = JSON.parse(data);
      console.log(data);
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
