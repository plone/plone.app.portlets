from .interfaces import IGroupDashboardPortletAssignmentMapping
from .interfaces import IPortletPermissionChecker
from .interfaces import IUserPortletAssignmentMapping
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.component import adapter
from zope.interface import implementer


@implementer(IPortletPermissionChecker)
@adapter(IPortletAssignmentMapping)
class DefaultPortletPermissionChecker:
    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        # If the user has the global Manage Portlets permission, let them
        # run wild
        if not sm.checkPermission("Portlets: Manage portlets", context):
            raise Unauthorized("You are not allowed to manage portlets")


@implementer(IPortletPermissionChecker)
@adapter(IUserPortletAssignmentMapping)
class UserPortletPermissionChecker:
    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        # If the user has the global Manage Portlets permission, let them
        # run wild
        if not sm.checkPermission("Portlets: Manage own portlets", context):
            raise Unauthorized("You are not allowed to manage portlets")

        user_id = sm.getUser().getId()

        if context.__name__ != user_id:
            raise Unauthorized("You are only allowed to manage your own portlets")


@implementer(IPortletPermissionChecker)
@adapter(IGroupDashboardPortletAssignmentMapping)
class GroupDashboardPortletPermissionChecker:
    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        if not sm.checkPermission("Portlets: Manage group portlets", context):
            raise Unauthorized("You are not allowed to manage group portlets")
