window.current_page = window.current_page || "1";
History.Adapter.bind(window, "statechange", function () {
    const State = History.getState();
    History.log("statechange:", State.data, State.title, State.url);
    $(".main_form").fadeOut(100);
    $(".loader").fadeIn(100);
    $.ajax({
        url: State.url,
        beforeSend: function (jqXHR, settings) {
            jqXHR.setRequestHeader("X-AJAX", "true");
        },
        success: function (result) {
            $(".loader").hide();
            $("#main").html(result);
        }
    });
    window.current_page = State.data.state;
    console.log(window.current_page);
});

$(document).ready(function () {
    $(document).on("click", ".pages a", function (e) {
        e.preventDefault();
        console.log("prevented click" + e);
        const page = $(this).attr("data-page");
        if (page !== undefined && page !== window.current_page.toString()) {
            History.pushState(
                {state: page},
                $(document).attr("title"),
                $(this).attr("href")
            );
        }
    });
});
