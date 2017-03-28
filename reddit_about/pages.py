from babel.numbers import format_currency
from pylons import app_globals as g
from pylons import tmpl_context as c
from pylons.i18n import _
from r2.lib.pages import Templated, BoringPage, FormPage
from r2.lib.menus import NavMenu, NavButton, OffsiteButton
from r2.lib.db.tdb_cassandra import NotFound
from r2.models import WikiPage, Frontpage
from reddit_about.models import SelfServeContent, SelfServeBlurb
from reddit_about.models import SelfServeAdvertiser, SelfServeQuote


class AboutPage(BoringPage):
    css_class = 'about-page'

    def __init__(self, content_id=None, title_msg=None, pagename=None, content=None, **kw):
        BoringPage.__init__(self, pagename or _('about reddit'), show_sidebar=False, content=content, **kw)
        self.content_id = content_id
        self.title_msg = title_msg

    def content(self):
        return self.content_stack([AboutTitle(self.title_msg), self._content])


class AboutTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message


class Postcards(Templated):
    pass
