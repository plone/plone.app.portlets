from .. import portlets
from ..interfaces import IDefaultDashboard
from ..storage import UserPortletAssignmentMapping
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletManager
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from zope.component import adapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.interface import implementer


def new_user(principal, event):
    """Initialise the dashboard for a new user"""
    defaults = IDefaultDashboard(principal, None)
    if defaults is None:
        return

    userid = principal.getId()
    portlets = defaults()

    for name in (
        "plone.dashboard1",
        "plone.dashboard2",
        "plone.dashboard3",
        "plone.dashboard4",
    ):
        assignments = portlets.get(name)
        if assignments:
            column = queryUtility(IPortletManager, name=name)
            if column is not None:
                category = column.get(USER_CATEGORY, None)
                if category is not None:
                    manager = category.get(userid, None)
                    if manager is None:
                        manager = category[userid] = UserPortletAssignmentMapping(
                            manager=name, category=USER_CATEGORY, name=userid
                        )
                    chooser = INameChooser(manager)
                    for assignment in assignments:
                        manager[chooser.chooseName(None, assignment)] = assignment


@implementer(IDefaultDashboard)
@adapter(IPropertiedUser)
class DefaultDashboard:
    """The default default dashboard."""

    def __init__(self, principal):
        self.principal = principal

    def __call__(self):
        return {
            "plone.dashboard1": (portlets.news.Assignment(),),
            "plone.dashboard2": (portlets.recent.Assignment(),),
            "plone.dashboard3": (),
            "plone.dashboard4": (portlets.review.Assignment(),),
        }
