/*jshint browser: true, nomen: false, eqnull: true, es5:true, trailing:true, 
  undef:true */
/*global jQuery, console, QUnit, COREMODELNS, window, alert */

(function ($) {

$(document).ready(function () {
  // Detect schema editor in DOM, inject script tag if applicable:
       if ($('form#add-field').length) {
    $('head').append(
      '<script type="text/javascript" src="++resource++orderedselect_input.js" />'
    );
  }
});

}(jQuery));
