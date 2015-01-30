!function(r, $) {
  'use strict';
  
  $(function() {
    $('a[href]').on('click', function(e) {
      var el = this;
      var $el = $(el);
      var href = $el.attr('href');
      var linkHost = href.match(/^https?:\/\/([^\/]+)/) && RegExp.$1;

      // only tracking external links
      if (linkHost === window.location.host) {
        return true;
      }

      // get the name of the nearest parent element with a selfserve-* css class
      // so the sales team can tell which instance of the link it is
      var parentClass = $el.closest('[class^=selfserve]').attr('class');
      var newTab = !!(el.target && el.target === '_blank');
      var callback = newTab ? undefined : function() {
        window.location.href = el.href;
      };

      r.analytics.fireGAEvent(
        'advertising',
        'external-link',
        _.compact([parentClass, href]).join(':'),
        undefined,
        undefined,
        callback);

      return newTab;
    });
  });
}(r, jQuery);
