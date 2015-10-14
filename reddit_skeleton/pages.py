
from pylons.i18n import _
from r2.lib.pages import Templated, BoringPage, FormPage
from r2.lib.menus import NavMenu, NavButton


class SkeletonPage(BoringPage):
    css_class = 'skeleton-page'

    def __init__(self, content_id=None, title_msg=None, pagename=None, content=None, **kw):
        BoringPage.__init__(self, pagename or _('skeleton reddit'), show_sidebar=False, content=content, **kw)
        self.content_id = content_id
        self.title_msg = title_msg

    def content(self):
        skeleton_buttons = [
            NavButton(_('Skeleton'), '/'),
        ]
        about_menu = NavMenu(skeleton_buttons, type='tabmenu', base_path='/skeleton/', css_class='skeleton-menu')
        return self.content_stack([SkeletonTitle(self.title_msg), about_menu, self._content])


class SkeletonTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message


class Skeleton(Templated):
    pass
