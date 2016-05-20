from r2.lib.plugin import Plugin
from r2.lib.configparse import ConfigValue
from r2.lib.js import Module
from r2.config.routing import not_in_sr


class About(Plugin):
    needs_static_build = True

    config = {
        ConfigValue.str: [
            'advertising_links_sr',
            'wiki_page_selfserve_advertisers',
            'wiki_page_selfserve_content',
            'wiki_page_selfserve_blurbs',
            'wiki_page_selfserve_quotes',
            'wiki_page_selfserve_help',
            'wiki_page_team_members',
        ],
    }

    js = {
        'about': Module('about.js',
            'lib/modernizr.custom.3d+shadow.js',
            'lib/iso8601.js',
            'slideshow.js',
            'timeline.js',
            'grid.js',
            'about.js',
            'about-main.js',
            'about-team.js',
            'about-postcards.js',
            prefix='about/',
        ),
        'advertising': Module('advertising.js',
            'advertising.js',
            prefix='advertising/',
        ),
    }

    def add_routes(self, mc):
        mc('/about/postcards', controller='about', action='postcards',
            conditions={'function': not_in_sr})
        # handle wildcard from postcard pushState URLs.
        mc('/about/postcards/*etc', controller='about', action='postcards',
            conditions={'function': not_in_sr})
        mc('/ad_inq', controller='redirect', action='redirect',
            dest='/advertising')
        mc('/advertising', controller='about', action='advertising', 
            conditions={'function':not_in_sr})

    def load_controllers(self):
        from about import AboutController
