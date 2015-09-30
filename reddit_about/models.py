from pylons import g

from r2.lib.template_helpers import (
    make_url_protocol_relative
)

from r2.models import Frontpage
from r2.models.wiki import WikiPageIniItem


class TeamMember(WikiPageIniItem):
    """Information about reddit team members."""

    _bool_values = WikiPageIniItem._bool_values + ("is_alumni",)

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_team_members

    def __init__(self, id, description, role, role_details, new,
            image_url, hover_image_url=None, favorite_subreddits=None,
            pyromania=None, height=None, wpm=None, is_alumni=False):
        self.is_enabled = True
        self.username = id
        self.description = description
        self.role = role
        self.role_details = role_details
        self.new = new
        self.image_url = image_url
        self.hover_image_url = hover_image_url
        if favorite_subreddits:
            self.favorite_subreddits = [sr.strip()
                for sr in favorite_subreddits.split(",")]
        else:
            favorite_subreddits = []
        self.pyromania = int(pyromania) if pyromania else None
        self.height = float(height) if height else None
        self.wpm = int(wpm) if wpm else None
        self.is_alumni = is_alumni


class SelfServeAdvertiser(WikiPageIniItem):
    """Information about reddit advertisers."""

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_selfserve_advertisers

    def __init__(self, id, name, url, image_url, is_enabled=True, **kwargs):
        self.id = id
        self.name = name
        self.url = url
        self.image_url = make_url_protocol_relative(image_url)
        self.is_enabled = is_enabled


class SelfServeContent(WikiPageIniItem):
    """Content for /advertising page."""

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_selfserve_content

    def __init__(self, id, title, text=None, is_enabled=True, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.is_enabled = is_enabled


class SelfServeBlurb(WikiPageIniItem):
    """Blurb about selfserve platform on /advertising page."""

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_selfserve_blurbs

    def __init__(self, id, title, text, is_enabled=True, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.is_enabled = is_enabled


class SelfServeQuote(WikiPageIniItem):
    """Blurb about selfserve platform on /advertising page."""

    @classmethod
    def _get_wiki_config(cls):
        return Frontpage, g.wiki_page_selfserve_quotes

    def __init__(self, id, text, cite, source, url, is_enabled=True, **kwargs):
        self.id = id
        self.text = text
        self.cite = cite
        self.source = source
        self.url = url
        self.is_enabled = is_enabled
