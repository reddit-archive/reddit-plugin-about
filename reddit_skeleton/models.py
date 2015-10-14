from pylons import app_globals as g

from r2.lib.template_helpers import (
    make_url_protocol_relative
)

from r2.models import Frontpage
from r2.models.wiki import WikiPageIniItem


class SkeletonModel(WikiPageIniItem):

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_skeleton_page

    def __init__(self, id, name, description):
        self.is_enabled = True
        self.username = id
        self.name = name
        self.description = description

