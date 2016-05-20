import re

from pylons import app_globals as g
from pylons.i18n import _

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.models import Subreddit
from r2.lib.validator import VNotInTimeout
from reddit_about.pages import Advertising, AdvertisingPage, Postcards, AboutPage
from r2.lib.pages.things import wrap_links
from r2.models import Link


@add_controller
class AboutController(RedditController):
    def GET_postcards(self):
        postcard_count = '&#32;<span class="count">...</span>&#32;'
        content = Postcards()
        return AboutPage(
            content_id='about-postcards',
            title_msg=_('you\'ve sent us over %s postcards.') % postcard_count,
            pagename=_('postcards'),
            content=content,
        ).render()

    def GET_advertising(self):
        VNotInTimeout().run(action_name="pageview", details_text="advertising")
        subreddit_links = self._get_selfserve_links(3)

        content = Advertising(
            subreddit_links=subreddit_links,
        )

        return AdvertisingPage(
            "advertise",
            content=content,
            loginbox=False,
            header=False,
        ).render()

    advertising_link_id36_re = re.compile("^.*/comments/(\w+).*$")

    def _get_selfserve_links(self, count):
        links = Subreddit._by_name(g.advertising_links_sr).get_links('new', 'all')
        items = Link._by_fullname(links, data=True, return_dict=False)
        id36s = map(lambda x: self.advertising_link_id36_re.match(x.url).group(1), items)
        ad_links = Link._byID36(id36s, return_dict=False, data=True)
        return wrap_links(ad_links, num=count)
