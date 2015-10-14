from pylons.i18n import _

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from reddit_skeleton.pages import (
    Skeleton,
    SkeletonPage,
)

@add_controller
class SkeletonController(RedditController):
    def GET_index(self):
        content = Skeleton()
        return SkeletonPage(
            content_id='skeleton-main',
            title_msg=_('skeleton page for reddit plugin'),
            pagename=_('skeleton plugin'),
            content=content,
        ).render()
