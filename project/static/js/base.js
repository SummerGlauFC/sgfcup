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
