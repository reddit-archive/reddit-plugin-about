!function(r, $) {
  'use strict';
  
  $(function() {
    // ugh. since this link is going to be hardcoded into the template _and_
    // added to the link section in the footer (which is markdown pulled from
    // a wiki page), I'm just going to attach events to all of the links on the
    // page containing 'redditadvertising' in the href since it works for both
    $('a[href*=redditadvertising]').on('click', function() {
      // get the name of the nearest parent element with a selfserve-* css class
      // so the sales team can tell which instance of the link it is
      var parentClass = $(this).closest('[class^=selfserve]').attr('class');
      r.analytics.fireGAEvent('advertising', 'contactLinkClicked', parentClass, this.href);
    });
  });
}(r, jQuery);
