from os import path
import json

from r2.lib.plugin import Plugin
from r2.lib.configparse import ConfigValue
from r2.lib.js import Module
from r2.config.routing import not_in_sr


class About(Plugin):
    needs_static_build = True

    config = {
        ConfigValue.int: [
            'about_images_count',
            'about_images_min_score',
        ],
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
        )
    }

    def add_routes(self, mc):
        # handle wildcard after /about/:action/ for postcard pushState URLs.
        for route in ('/about/:action', '/about/:action/*etc'):
            mc(route, controller='about', conditions={'function':not_in_sr},
               requirements={'action':'team|postcards|alien'})
        mc('/ad_inq', controller='redirect', action='redirect',
            dest='/advertising')
        mc('/advertising', controller='about', action='advertising', 
            conditions={'function':not_in_sr})

    def load_controllers(self):
        def load(name):
            with open(path.join(path.dirname(__file__), 'data', name)) as f:
                data = json.load(f)
            return data

        from about import AboutController, parse_date_text
        self.timeline_data = load('timeline.json')
        for idx, event in enumerate(self.timeline_data):
            self.timeline_data[idx]['date'] = parse_date_text(event['date'])
        self.sites_data = load('sites.json')
        self.colors_data = load('colors.json')
