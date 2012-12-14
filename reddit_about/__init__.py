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
            'about_images_min_score'
        ]
    }

    js = {
        'less': Module('less.js',
            'lib/less-1.3.0.min.js',
            prefix='about/',
            should_compile=False
        ),

        'about': Module('about.js',
            'lib/modernizr.custom.3d+shadow.js',
            'lib/underscore-1.3.3.js',
            'lib/backbone-0.9.2.js',
            'lib/iso8601.js',
            'about-utils.js',
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
            mc(route, controller='about', conditions={'function':not_in_sr})

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
        self.team_data = load('team.json')
        self.colors_data = load('colors.json')

