window.current_page = window.current_page || "1";
History.Adapter.bind(window, "statechange", function() {
  var State = History.getState();
  History.log("statechange:", State.data, State.title, State.url);
  $(".main_form").fadeOut(100);
  $(".loader").fadeIn(100);
  $.ajax({
    url: State.url,
    beforeSend: function(jqXHR, settings) {
      jqXHR.setRequestHeader("X-AJAX", "true");
    },
    success: function(result) {
      $(".loader").hide();
      $("#main").html(result);
    }
  });
  window.current_page = State.data.state;
  console.log(window.current_page);
});

$(document).ready(function() {
  $(document).on("click", ".pages a", function(e) {
    e.preventDefault();
    console.log("prevented click" + e);
    if ($(this).attr("data-page") !== undefined) {
      console.log($(this).attr("data-page") + " != " + window.current_page);

      a_this = $(this);

      if ($(this).attr("data-page") != window.current_page) {
        History.pushState(
          { state: $(this).attr("data-page") },
          $(document).attr("title"),
          $(this).attr("href")
        );
      }
    }
  });
});
