r.about = { pages: {} }

// Set the Underscore template data object name to 'd'.
// see http://documentcloud.github.com/underscore/#template
_.extend(_.templateSettings, {
    variable: 'd'
})

$(function() {
    var page = $('.content.about-page')
    if (page) {
        var init = init = r.about.pages[page.attr('id')]
        if (init) { init() }
    }
})
