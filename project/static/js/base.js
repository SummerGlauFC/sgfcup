const wrapper = $("#wrapper");
$.fn.equalHeight = function () {
    let max = 0;
    return this.children()
        .each(function () {
            const height = $(this).height();
            max = height > max ? height : max;
        })
        .height(max);
};
$(window).resize(function () {
    wrapper.equalHeight();
});
$(document).ready(function () {
    wrapper.equalHeight();
});
$("#clear-fields").on("click", function () {
    $("#key")
        .get(0)
        .setAttribute("value", "");
    $("#password")
        .get(0)
        .setAttribute("value", "");
});