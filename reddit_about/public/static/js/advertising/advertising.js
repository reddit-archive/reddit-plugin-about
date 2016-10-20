!function(r, $) {
  'use strict';

  var _getActionDetails = r.login.ui._getActionDetails;
  var _showLogin = r.ui.LoginPopup.prototype.showLogin;

  r.login.ui._getActionDetails = function(el) {
    var $el = $(el);
    var details = $el.data('action-details');

    if (details) {
      return details;
    }

    return _getActionDetails.apply(this, arguments);
  };

  r.ui.LoginPopup.prototype.showLogin = function() {
    var $email = this.$.find('[name=email]');
    var $form = $email.closest('form');
    var label = r._('email');

    $form.append('<input type="hidden" name="sponsor" value="true">');

    $email
      .attr('placeholder', label)
      .data('validate-url', '/api/check_email.json?sponsor=true')
      .data('validate-noclear', true);
    $email.closest('.c-form-group')
      .find('label')
      .text(label);

    return _showLogin.apply(this, arguments);
  };
  
  $(function() {
    $('a[href]:not(.login-required)').on('click', function(e) {
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

  $(function() {
    var conversion = document.createElement('img');

    conversion.onload = conversion.onerror = changeLocation;
    conversion.src = '//engine.a.redditmedia.com/e/5146/130267/e.gif?_=' + (new Date().getTime());
  });

}(r, jQuery);
