from os import path
import json

from r2.lib.plugin import Plugin
from r2.lib.configparse import ConfigValue
from r2.lib.js import Module

class About(Plugin):
    needs_static_build = True

    config = {
        ConfigValue.int: [
            'skeleton_int',
        ],
        ConfigValue.str: [
            'skeleton_str',
        ],
    }

    js = {
        'skeleton': Module('skeleton.js',
        ),
    }

    def add_routes(self, mc):
        mc('/skeleton', controller='skeleton', action='foo', )

    def load_controllers(self):
        def load(name):
            with open(path.join(path.dirname(__file__), 'data', name)) as f:
                data = json.load(f)
            return data

        from about import AboutController, parse_date_text
        self.sites_data = load('skeleton.json')

