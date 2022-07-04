from ..interfaces import IPortletPermissionChecker
from ..interfaces import ITopbarManagePortlets
from ..storage import GroupDashboardPortletAssignmentMapping
from ..storage import PortletAssignmentMapping
from ..storage import UserPortletAssignmentMapping
from .interfaces import IManageContentTypePortletsView
from .interfaces import IManageContextualPortletsView
from .interfaces import IManageDashboardPortletsView
from .interfaces import IManageGroupPortletsView
from .interfaces import IManagePortletsView
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.portlets import utils
from plone.memoize.view import memoize
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.protect.authenticator import createToken
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import implementer_only
from zope.publisher.interfaces.browser import IBrowserView


@implementer(IManageContextualPortletsView)
class ManageContextualPortlets(BrowserView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.request.set("disable_border", True)

    # IManagePortletsView implementation

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return CONTEXT_CATEGORY

    @property
    def key(self):
        return "/".join(self.context.getPhysicalPath())

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        return f"{baseUrl}/++contextportlets++{manager.__name__}"

    def getAssignmentsForManager(self, manager):
        assignments = getMultiAdapter(
            (self.context, manager), IPortletAssignmentMapping
        )
        return assignments.values()

    # view @@manage-portlets

    def has_legacy_portlets(self):
        left_slots = getattr(aq_base(self.context), "left_slots", [])
        right_slots = getattr(aq_base(self.context), "right_slots", [])

        return left_slots or right_slots

    # view @@set-portlet-blacklist-status
    def set_blacklist_status(
        self, manager, group_status, content_type_status, context_status
    ):
        authenticator = getMultiAdapter(
            (self.context, self.request), name="authenticator"
        )
        if not authenticator.verify():
            raise Unauthorized
        portletManager = getUtility(IPortletManager, name=manager)
        assignable = getMultiAdapter(
            (self.context, portletManager), ILocalPortletAssignmentManager
        )
        assignments = getMultiAdapter(
            (self.context, portletManager), IPortletAssignmentMapping
        )

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        def int2status(status):
            if status == 0:
                return None
            elif status > 0:
                return True
            else:
                return False

        assignable.setBlacklistStatus(GROUP_CATEGORY, int2status(group_status))
        assignable.setBlacklistStatus(
            CONTENT_TYPE_CATEGORY, int2status(content_type_status)
        )
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, int2status(context_status))

        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        self.request.response.redirect(baseUrl + "/@@manage-portlets")
        return ""

    # view @@convert-legacy-portlets

    def convert_legacy_portlets(self):
        utils.convert_legacy_portlets(self.context)
        self.request.response.redirect(
            self.context.absolute_url() + "/@@manage-portlets"
        )


@implementer(IManageDashboardPortletsView)
class ManageDashboardPortlets(BrowserView):

    # IManagePortletsView implementation

    @property
    def auth_token(self):
        return createToken()

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return USER_CATEGORY

    @property
    def key(self):
        return self._getUserId()

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        userId = self._getUserId()
        return f"{baseUrl}/++dashboard++{manager.__name__}+{userId}"

    def getAssignmentsForManager(self, manager):
        userId = self._getUserId()
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[USER_CATEGORY]
        mapping = category.get(userId, None)
        if mapping is None:
            mapping = category[userId] = UserPortletAssignmentMapping(
                manager=manager.__name__, category=USER_CATEGORY, name=userId
            )
        return mapping.values()

    def _getUserId(self):
        membership = getToolByName(aq_inner(self.context), "portal_membership", None)
        if membership.isAnonymousUser():
            raise Unauthorized(
                "Cannot get portlet assignments for anonymous " "through this view"
            )

        member = membership.getAuthenticatedMember()
        memberId = member.getId()

        if memberId is None:
            raise KeyError("Cannot find user id of current user")

        return memberId


@implementer(IManageDashboardPortletsView)
class ManageGroupDashboardPortlets(BrowserView):
    @property
    def group(self):
        return self.request.get("key", None)

    # IManagePortletsView implementation

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return GROUP_CATEGORY

    @property
    def key(self):
        return self.group

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        return f"{baseUrl}/++groupdashboard++{manager.__name__}+{self.group}"

    def getAssignmentsForManager(self, manager):
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(self.group, None)
        if mapping is None:
            mapping = category[self.group] = GroupDashboardPortletAssignmentMapping(
                manager=manager.__name__, category=GROUP_CATEGORY, name=self.group
            )
        return mapping.values()


@implementer(IManageGroupPortletsView)
class ManageGroupPortlets(BrowserView):

    # IManagePortletsView implementation

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return GROUP_CATEGORY

    @property
    def key(self):
        return self.request["key"]

    def __init__(self, context, request):
        super().__init__(context, request)
        self.request.set("disable_border", True)

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        key = self.request["key"]
        return f"{baseUrl}/++groupportlets++{manager.__name__}+{key}"

    def getAssignmentsForManager(self, manager):
        key = self.request["key"]
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(key, None)
        if mapping is None:
            mapping = category[key] = PortletAssignmentMapping(
                manager=manager.__name__, category=GROUP_CATEGORY, name=key
            )
        return mapping.values()

    # View attributes

    def group(self):
        return self.request["key"]


@implementer(IManageContentTypePortletsView)
class ManageContentTypePortlets(BrowserView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.request.set("disable_border", True)

    # IManagePortletsView implementation

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return CONTENT_TYPE_CATEGORY

    @property
    def key(self):
        return self.request["key"]

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        pt = self.request["key"]
        return f"{baseUrl}/++contenttypeportlets++{manager.__name__}+{pt}"

    def getAssignmentsForManager(self, manager):
        pt = self.request["key"]
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[CONTENT_TYPE_CATEGORY]
        mapping = category.get(pt, None)
        if mapping is None:
            mapping = category[pt] = PortletAssignmentMapping(
                manager=manager.__name__, category=CONTENT_TYPE_CATEGORY, name=pt
            )
        return mapping.values()

    # View attributes

    def portal_type(self):
        return self.fti().Title()

    def portal_type_icon(self):
        plone_layout = getMultiAdapter(
            (self.context, self.request), name="plone_layout"
        )
        return plone_layout.getIcon(self.fti())

    @memoize
    def fti(self):
        portal_types = getToolByName(aq_inner(self.context), "portal_types")
        portal_type = self.request["key"]
        for fti in portal_types.listTypeInfo():
            if fti.getId() == portal_type:
                return fti


@implementer(IManagePortletsView)
class ManagePortletsViewlet(BrowserView):
    """A general base class for viewlets that want to be rendered on the
    manage portlets view. This makes it possible to have a viewlet that
    renders a portlet manager, and still have the generic edit manager
    renderer work (it doesn't work otherwise, because the edit manager
    renderer is registered on IManagePortletsView, but inside a viewlet,
    the __parent__ is the viewlet, not the ultimate parent).
    """

    def __init__(self, context, request, view, manager):
        super().__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return self.ultimate_parent().category

    @property
    def key(self):
        return self.ultimate_parent().key

    def __getattribute__(self, name):
        # Products.Five.viewlet.viewlet.SimpleViewletClass redefines __name__
        # so a simple property or attribute does not work
        if name == "__name__":
            return self.ultimate_parent().__name__
        return super().__getattribute__(name)

    def getAssignmentMappingUrl(self, manager):
        return self.ultimate_parent().getAssignmentMappingUrl(manager)

    def getAssignmentsForManager(self, manager):
        return self.ultimate_parent().getAssignmentsForManager(manager)

    @memoize
    def ultimate_parent(self):
        # Walk the __parent__ chain to find the principal view
        parent = self.__parent__
        while hasattr(parent, "__parent__") and IBrowserView.providedBy(
            parent.__parent__
        ):
            parent = parent.__parent__
        return parent

    # Subclasses need to implement update() and render() - or
    # we can use ZCML with the template attribute (hence we don't
    # put these here)


@implementer(IManageContextualPortletsView)
class ManageContextualPortletsViewlet(ManagePortletsViewlet):
    """A viewlet base class for viewlets that need to render on the
    manage contextual portlets screen.
    """


@implementer(IManageGroupPortletsView)
class ManageGroupPortletsViewlet(ManagePortletsViewlet):
    """A viewlet base class for viewlets that need to render on the
    manage group portlets screen.
    """


@implementer(IManageContentTypePortletsView)
class ManageContentTypePortletsViewlet(ManagePortletsViewlet):
    """A viewlet base class for viewlets that need to render on the
    manage content type portlets screen.
    """


@implementer_only(ITopbarManagePortlets)
class TopbarManagePortlets(ManageContextualPortlets):
    def __init__(self, context, request):
        super().__init__(context, request)
        # Disable the left and right columns
        self.request.set("disable_plone.leftcolumn", 1)
        self.request.set("disable_plone.rightcolumn", 1)
        # Initialize the manager name in case there is nothing
        # in the traversal path
        self.manager_name = "plone.leftcolumn"

    def publishTraverse(self, request, name):
        """Get the portlet manager via traversal so that we can re-use
        the portlet machinery without overriding it all here.
        """
        self.manager_name = name
        return self

    def render_edit_manager_portlets(self):
        # Pay attention again
        # Here we manually render the portlets instead of doing
        # something like provider:${view/manager_name} in the template
        manager_view = ManageContextualPortlets(self.context, self.request)
        manager_view.__name__ = "manage-portlets"
        portlet_manager = getMultiAdapter(
            (self.context, self.request, manager_view), name=self.manager_name
        )
        portlet_manager.update()
        return portlet_manager.render()
