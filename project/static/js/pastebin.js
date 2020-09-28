const form = $("form");
form.submit(function () {
    $("textarea").hide();
    $.ajax({
        type: "POST",
        url: form.attr("action"),
        data: $("form").serialize(),
        success: function (data) {
            const msg = $("#message");
            if (data.success) {
                msg.html(
                    '<a href="' + data.url + '">' + data.base + data.url + "</a>"
                );
            } else {
                msg.html(data.error);
            }
            msg.fadeIn(250);
        }
    });
    return false;
});
