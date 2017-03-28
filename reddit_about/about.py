import re

from pylons import app_globals as g
from pylons.i18n import _

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.models import Subreddit
from r2.lib.validator import VNotInTimeout
from reddit_about.pages import Postcards, AboutPage
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
