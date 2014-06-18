import random
import string

from babel.numbers import format_currency
from pylons import request, g, c
from pylons.i18n import _
from r2.lib.pages import Templated, BoringPage, FormPage
from r2.lib.menus import NavMenu, NavButton, OffsiteButton
from r2.models import WikiPage, Frontpage
from reddit_about.models import *

class AboutPage(BoringPage):
    css_class = 'about-page'

    def __init__(self, content_id=None, title_msg=None, pagename=None, content=None, **kw):
        BoringPage.__init__(self, pagename or _('about reddit'), show_sidebar=False, content=content, **kw)
        self.content_id = content_id
        self.title_msg = title_msg

    def content(self):
        about_buttons = [
            NavButton(_('about reddit'), '/'),
            NavButton(_('team'), '/team'),
            NavButton(_('postcards'), '/postcards'),
            NavButton(_('alien'), '/alien'),
            #NavButton(_('guide'), '/guide')
        ]
        about_menu = NavMenu(about_buttons, type='tabmenu', base_path='/about/', css_class='about-menu')
        return self.content_stack([AboutTitle(self.title_msg), about_menu, self._content])


class AboutTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message


class About(Templated):
    pass


class Team(Templated):
    def __init__(self, team, alumni, sorts, extra_sorts):
        Templated.__init__(self, team=team, alumni=alumni, sorts=sorts + extra_sorts)

        sort_buttons = []
        extra_sort_index = random.randint(len(sorts), len(self.sorts)-1)
        for idx, sort in enumerate(self.sorts):
            css_class = 'choice-'+sort['id']
            if sort in extra_sorts and idx != extra_sort_index:
                css_class += ' hidden-sort'
            button = OffsiteButton(sort['title'], '#sort/'+sort['id'], css_class=css_class)
            sort_buttons.append(button)
        self.sort_menu = NavMenu(sort_buttons, title=_('sorted by'), base_path=request.path, type='lightdrop', default='#sort/random')

        # The caching check won't catch the hidden-sort classes
        self.sort_menu.cachable = False


class AdvertisingPage(FormPage):
    pass


class Postcards(Templated):
    pass


class AlienMedia(Templated):
    pass


class Advertising(Templated):
    def __init__(self, *args, **kwargs):
        nav_buttons = [
            NavButton(_('overview'), '/advertising'),
            OffsiteButton(_('getting started'), 'http://www.redditstatic.com/ads/reddit-Advertising-Manual.pdf'),
            NavButton(_('audience'), '/wiki/mediakit'),
            NavButton(_('best practices'), '/wiki/selfserve#wiki_what_are_the_best_practices_for_reddit_advertising.3F'),
            NavButton(_('help center'), '/wiki/selfserve'),
            NavButton(_('manage ads'), '/promoted'),
        ]

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
            formatted_cpm = format_currency(g.cpm_selfserve.decimal, 'USD', locale=c.locale)
            formatted_min_bid = format_currency(g.min_promote_bid, 'USD', locale=c.locale)
            blurbs['platform'].text = blurbs['platform'].text.replace(
                '[min_promote_bid]', formatted_min_bid).replace(
                '[cpm_selfserve]', formatted_cpm)
        self.blurbs = blurbs.values()
        self.advertiser_logos = SelfServeAdvertiser.get_all()
        self.quotes = SelfServeQuote.get_all()
        self.help_text = WikiPage.get(Frontpage, g.wiki_page_selfserve_help).content
        Templated.__init__(self, *args, **kwargs)
