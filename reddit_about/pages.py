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



class AdvertisingPage(FormPage):
    pass


class Postcards(Templated):
    pass


class Advertising(Templated):
    def __init__(self, *args, **kwargs):
        nav_buttons = [
            NavButton(_('overview'), '/advertising'),
            OffsiteButton(_('getting started'), 'https://reddit.zendesk.com/hc/en-us/articles/205118995-Step-by-step-How-to-create-an-ad'),
            OffsiteButton(_('audience'), 'https://reddit.zendesk.com/hc/en-us/articles/205183225-Audience-and-Demographics'),
            OffsiteButton(_('best practices'), 'https://reddit.zendesk.com/hc/en-us/sections/200863319-Best-Practices-Tips'),
            OffsiteButton(_('help center'), 'https://reddit.zendesk.com/hc/en-us/categories/200352595-Advertising-'),
            NavButton(_('manage ads'), '/promoted?utm_source=advertising&utm_medium=button&utm_term=manage%20ads&utm_campaign=buttons'),
        ]

        self.create_ad_url = '/promoted/new_promo?utm_source=advertising&utm_medium=button&utm_term=create%20ads&utm_campaign=buttons'

        self.nav_menu = NavMenu(nav_buttons,
            type='flatlist',
            base_path='',
            css_class='advertising-menu',
            separator=None).render()

        sections = SelfServeContent.get_all(return_dict=True)
        self.banner = sections.get('banner')
        self.info = sections.get('info')
        self.advertisers = sections.get('advertisers')
        self.subreddit = sections.get('subreddit')
        self.help = sections.get('help')
        blurbs = SelfServeBlurb.get_all(return_dict=True)
        if 'platform' in blurbs:
            min_cpm = min([
                g.cpm_selfserve_collection.decimal,
                g.cpm_selfserve.decimal,
                g.cpm_selfserve_geotarget_metro.decimal,
            ])
            formatted_min_cpm = format_currency(min_cpm, 'USD', locale=c.locale)
            formatted_min_budget = format_currency(
                g.min_total_budget_pennies / 100., 'USD', locale=c.locale)
            blurbs['platform'].text = blurbs['platform'].text.replace(
                '[min_promote_bid]', formatted_min_budget).replace(
                '[cpm_selfserve]', formatted_min_cpm)
        self.blurbs = blurbs.values()
        self.advertiser_logos = SelfServeAdvertiser.get_all()
        self.quotes = SelfServeQuote.get_all()
        self.help_text = None
        try:
            self.help_text = WikiPage.get(Frontpage, g.wiki_page_selfserve_help).content
        except NotFound:
            pass
        Templated.__init__(self, *args, **kwargs)
