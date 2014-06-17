from pylons import g
from r2.models import Frontpage
from r2.models.wiki import WikiPageIniItem

class SelfServeAdvertiser(WikiPageIniItem):
    """Information about reddit advertisers."""
    _wiki_page_name = g.wiki_page_selfserve_advertisers
    _sr = Frontpage

    def __init__(self, id, name, url, image_url, is_enabled=True, **kwargs):
        self.id = id
        self.name = name
        self.url = url
        self.image_url = image_url
        self.is_enabled = is_enabled


class SelfServeContent(WikiPageIniItem):
    """Content for /advertising page."""
    _wiki_page_name = g.wiki_page_selfserve_content
    _sr = Frontpage

    def __init__(self, id, title, text=None, is_enabled=True, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.is_enabled = is_enabled


class SelfServeBlurb(WikiPageIniItem):
    """Blurb about selfserve platform on /advertising page."""
    _wiki_page_name = g.wiki_page_selfserve_blurbs
    _sr = Frontpage

    def __init__(self, id, title, text, is_enabled=True, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.is_enabled = is_enabled


class SelfServeQuote(WikiPageIniItem):
    """Blurb about selfserve platform on /advertising page."""
    _wiki_page_name = g.wiki_page_selfserve_quotes
    _sr = Frontpage

    def __init__(self, id, text, cite, source, url, is_enabled=True, **kwargs):
        self.id = id
        self.text = text
        self.cite = cite
        self.source = source
        self.url = url
        self.is_enabled = is_enabled
