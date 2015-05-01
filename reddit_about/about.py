import re
import random
from os import path
from itertools import chain
from datetime import datetime

from pylons import g, c
from pylons.i18n import _

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.models import Subreddit
from r2.models.builder import IDBuilder
from r2.models.keyvalue import NamedGlobals
from r2.lib.db.queries import CachedResults
from r2.lib.template_helpers import static, comment_label
from reddit_about.models import TeamMember
from reddit_about.pages import (
    About,
    AboutPage,
    AboutTitle,
    Advertising,
    AdvertisingPage,
    AlienMedia,
    Postcards,
    Team,
    Values,
)
from r2.lib.pages.things import wrap_links
from r2.models import Link, WikiPage

def parse_date_text(date_str):
    if not date_str:
        return None

    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        parsed_date = None
    else:
        # Fudge timezone to g.tz
        parsed_date = parsed_date.replace(tzinfo=g.tz)

    return parsed_date


@add_controller
class AboutController(RedditController):
    def GET_index(self):
        quote = self._get_quote()
        images = self._get_images()
        stats = NamedGlobals.get('about_reddit_stats', None)
        c.js_preload.set('#images', images)
        content = About(
            quote=quote,
            images=images,
            stats=stats,
            events=g.plugins['about'].timeline_data,
            sites=g.plugins['about'].sites_data,
        )
        return AboutPage(
            content_id='about-main',
            title_msg=_('we power awesome communities.'),
            pagename=_('about reddit'),
            content=content,
        ).render()

    def GET_team(self):
        sort_names = ["random", "username", "new", "height", "pyromania", "wpm"]
        sorts = {name: {"id": name, "title": name, "dir": -1}
            for name in sort_names}
        sorts["height"]["title"] = "top"
        sorts["wpm"]["title"] = "words per minute"
        sorts["username"]["dir"] = 1

        all_members = TeamMember.get_all()
        team = [member for member in all_members if not member.is_alumni]
        alumni = [member for member in all_members if member.is_alumni]

        c.js_preload.set('#sorts', sorts.values())
        c.js_preload.set('#team', [member.__dict__ for member in team])
        c.js_preload.set('#alumni', [member.__dict__ for member in alumni])

        content = Team(sorts, team, alumni)

        return AboutPage(
            content_id='about-team',
            title_msg=_('we spend our days building reddit.'),
            pagename=_('about the reddit team'),
            content=content,
        ).render()

    def GET_postcards(self):
        postcard_count = '&#32;<span class="count">...</span>&#32;'
        content = Postcards()
        return AboutPage(
            content_id='about-postcards',
            title_msg=_('you\'ve sent us over %s postcards.') % postcard_count,
            pagename=_('postcards'),
            content=content,
        ).render()

    def GET_alien(self):
        content = AlienMedia(colors=g.plugins['about'].colors_data)
        return AboutPage(
            content_id='about-alien',
            title_msg=_('I also do birthday parties.'),
            pagename=_('the alien'),
            content=content,
        ).render()

    def GET_guide(self):
        return AboutPage(
            content_id='about-guide',
            title_msg=_('new to reddit? welcome.'),
            pagename=_('guide'),
        ).render()

    def GET_values(self):
        content = Values()
        return AboutPage(
            content_id='about-values',
            title_msg=_('these are our core values'),
            pagename=_('values'),
            content=content,
        ).render()

    def GET_advertising(self):
        subreddit_links = self._get_selfserve_links(3)

        content = Advertising(
            subreddit_links=subreddit_links,
        )

        return AdvertisingPage(
            "advertise",
            content=content,
            loginbox=False,
        ).render()

    advertising_link_id36_re = re.compile("^.*/comments/(\w+).*$")

    def _get_selfserve_links(self, count):
        links = Subreddit._by_name(g.advertising_links_sr).get_links('new', 'all')
        items = Link._by_fullname(links, data=True, return_dict=False)
        id36s = map(lambda x: self.advertising_link_id36_re.match(x.url).group(1), items)
        ad_links = Link._byID36(id36s, return_dict=False, data=True)
        return wrap_links(ad_links, num=count)

    def _get_hot_posts(self, sr, count, shuffle=False, filter=None):
        links = sr.get_links('hot', 'all')
        assert type(links) is CachedResults
        ids = list(links)
        if shuffle:
            random.shuffle(ids)
        builder = IDBuilder(ids, skip=True,
                            keep_fn=filter,
                            num=count)
        return builder.get_items()[0]

    quote_title_re = re.compile(r'''
        ^
        "(?P<body>[^"]+)"\s*                # "quote"
        --\s*(?P<author>[^,[]+)             # --author
        (?:,\s*(?P<date>\d+/\d+/\d+))?      # , mm/dd/yy *optional*
        \s*(?:\[via\s*(?P<via>[^\]]+)\])?   # [via username] *optional*
        $
    ''', re.VERBOSE)

    def _get_quote(self):
        sr = Subreddit._by_name(g.about_sr_quotes)
        quote_link = self._get_hot_posts(sr, count=1, shuffle=True,
            filter=lambda x: self.quote_title_re.match(x.title))[0]

        quote = self.quote_title_re.match(quote_link.title).groupdict()
        quote['date'] = parse_date_text(quote['date']) or quote_link._date
        quote['url'] = quote_link.url
        quote['author_url'] = getattr(quote_link, 'author_url', quote['url'])
        quote['via'] = quote['via'] or quote_link.author.name
        quote['via_url'] = '/user/' + quote['via']
        quote['comment_label'], quote['comment_class'] = \
                comment_label(quote_link.num_comments)
        quote['permalink'] = quote_link.permalink
        return quote

    image_title_re = re.compile(r'''
        ^
        (?P<title>[^[]+?)\s*                # photo title
        \s*(?:\[by\s*(?P<author>[^\]]+)\])  # [by author]
        \s*(?:\[via\s*(?P<via>[^\]]+)\])?   # [via username] *optional*
        $
    ''', re.VERBOSE)

    def _get_images(self):
        sr = Subreddit._by_name(g.about_sr_images)
        image_links = self._get_hot_posts(sr, count=g.about_images_count,
            filter=lambda x: self.image_title_re.match(x.title)
                             and x.score >= g.about_images_min_score)

        images = []
        for image_link in image_links:
            image = self.image_title_re.match(image_link.title).groupdict()
            image['url'] = image_link.url
            default_src = static('about/slideshow/%s.jpg' % image_link._id36)
            image['src'] = getattr(image_link, 'slideshow_src', default_src)
            image['author_url'] = getattr(image_link, 'author_url', image['url'])
            image['via'] = image['via'] or image_link.author.name
            image['via_url'] = '/user/' + image['via']
            image['comment_label'], image['comment_class'] = \
                    comment_label(image_link.num_comments)
            image['permalink'] = image_link.permalink
            images.append(image)
        return images
