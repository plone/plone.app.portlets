from Acquisition import aq_base
from plone.app.event.portlets import portlet_calendar as calendar
from plone.app.event.portlets import portlet_events as events
from plone.app.portlets import HAS_PLONE_APP_EVENT
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.portlets import classic
from plone.app.portlets.portlets import login
from plone.app.portlets.portlets import navigation
from plone.app.portlets.portlets import news
from plone.app.portlets.portlets import recent
from plone.app.portlets.portlets import review
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.storage import UserPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.container.interfaces import INameChooser


def assignment_mapping_from_key(context, manager_name, category, key, create=False):
    """Given the name of a portlet manager, the name of a category, and a
    key in that category, return the IPortletAssignmentMapping.
    Raise a KeyError if it cannot be found.
    """

    manager = getUtility(IPortletManager, manager_name)

    if category == CONTEXT_CATEGORY:
        path = key
        portal = getToolByName(context, "portal_url").getPortalObject()
        portal_path = "/".join(portal.getPhysicalPath())
        if path == portal_path:
            # there may be problem if PloneSite id is 'plone'.
            # restrictedTraverse traverses to @@plone BrowserView which
            # is wrong
            obj = portal
        else:
            if path.startswith(portal_path + "/"):
                path = path[len(portal_path) + 1 :]
            while path.startswith("/"):
                path = path[1:]
            obj = portal.restrictedTraverse(path, None)
        if obj is None:
            raise KeyError("Cannot find object at path %s" % path)
        return getMultiAdapter((obj, manager), IPortletAssignmentMapping)
    else:
        mapping = manager[category]
        if key not in mapping and create:
            if category == USER_CATEGORY:
                mapping[key] = UserPortletAssignmentMapping()
            else:
                mapping[key] = PortletAssignmentMapping()
        return mapping[key]


def assignment_from_key(context, manager_name, category, key, name):
    """Given the name of a portlet manager, the name of a category, a
    key in that category and the name of a particular assignment, return
    the IPortletAssignment. Raise a KeyError if it cannot be found.
    """
    return assignment_mapping_from_key(context, manager_name, category, key)[name]


DONT_MIGRATE = object()


def convert_legacy_portlets(context):
    """Convert legacy portlets (left_slots, right_slots) in the given
    context to new-style portlets.
    """

    portletsMapping = {
        "portlet_login": login.Assignment(),
        "portlet_news": news.Assignment(count=5),
        "portlet_navigation": navigation.Assignment(),
        "portlet_review": review.Assignment(),
        "portlet_recent": recent.Assignment(count=5),
        "portlet_related": DONT_MIGRATE,
        "portlet_languages": DONT_MIGRATE,
        "portlet_calendar": DONT_MIGRATE,
        "portlet_events": DONT_MIGRATE,
        "portlet_calendar": calendar.Assignment(),
        "portlet_events": events.Assignment(count=5),
    }

    # Convert left_slots and right_slots to portlets

    left = getUtility(IPortletManager, name="plone.leftcolumn")
    right = getUtility(IPortletManager, name="plone.rightcolumn")

    leftAssignable = getMultiAdapter((context, left), IPortletAssignmentMapping).__of__(
        context
    )
    rightAssignable = getMultiAdapter(
        (context, right), IPortletAssignmentMapping
    ).__of__(context)

    IPortletPermissionChecker(leftAssignable)()
    IPortletPermissionChecker(rightAssignable)()

    leftChooser = INameChooser(leftAssignable)
    rightChooser = INameChooser(rightAssignable)

    left_slots = getattr(aq_base(context), "left_slots", [])
    right_slots = getattr(aq_base(context), "right_slots", [])

    for item in left_slots:
        path = item.split("/")
        if len(path) == 4:
            newPortlet = portletsMapping.get(path[1], None)
            if (
                newPortlet is None
                and path[0] in ("context", "here")
                and path[2] == "macros"
            ):
                newPortlet = classic.Assignment(path[1], path[3])
            if newPortlet is not None and newPortlet is not DONT_MIGRATE:
                leftAssignable[leftChooser.chooseName(None, newPortlet)] = newPortlet

    for item in right_slots:
        path = item.split("/")
        if len(path) == 4:
            newPortlet = portletsMapping.get(path[1], None)
            if (
                newPortlet is None
                and path[0] in ("context", "here")
                and path[2] == "macros"
            ):
                newPortlet = classic.Assignment(path[1], path[3])
            if newPortlet is not None and newPortlet is not DONT_MIGRATE:
                rightAssignable[rightChooser.chooseName(None, newPortlet)] = newPortlet

    context.left_slots = []
    context.right_slots = []
