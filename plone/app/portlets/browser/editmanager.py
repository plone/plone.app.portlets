from ..interfaces import IDashboard
from ..interfaces import IPortletPermissionChecker
from .interfaces import IManageColumnPortletsView
from .interfaces import IManageContextualPortletsView
from .interfaces import IManageDashboardPortletsView
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import Explicit
from Acquisition.interfaces import IAcquirer
from five.customerize.zpt import TTWViewTemplateRenderer
from plone.memoize.view import memoize
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletContext
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.utils import hashPortletInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote
from Products.PythonScripts.standard import url_unquote
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.container import contained
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import logging


@implementer(IPortletManagerRenderer)
@adapter(Interface, IDefaultBrowserLayer, IManageColumnPortletsView, IPortletManager)
class EditPortletManagerRenderer(Explicit):
    """Render a portlet manager in edit mode.

    This is the generic renderer, which delegates to the view to determine
    which assignments to display.

    """

    template = ViewPageTemplateFile("templates/edit-manager.pt")

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.manager = manager  # part of interface
        self.context = context
        self.request = request
        self.__updated = False

    @property
    def visible(self):
        return True

    def filter(self, portlets):
        return portlets

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return self.template()

    # Used by the view template

    @property
    def view_name(self):
        name = self.__parent__.__name__
        if not name:
            # try to fallback on the 'name' attribute for
            # TTW customized views, see #11409
            if "TTWView" in self.__parent__.__class__.__name__:
                try:
                    path = self.request.get("PATH_INFO")
                    template_renderer = self.request.traverse(path)
                    name = getattr(template_renderer.template, "view_name", None)
                except (
                    AttributeError,
                    KeyError,
                    Unauthorized,
                ):
                    logging.getLogger("plone.app.portlets.browser").debug(
                        "Cant get view name for TTV %s" % self.__parent__
                    )
        return name

    def normalized_manager_name(self):
        return self.manager.__name__.replace(".", "-")

    def baseUrl(self):
        return self.__parent__.getAssignmentMappingUrl(self.manager)

    def portlets(self):
        assignments = self._lazyLoadAssignments(self.manager)
        return self.portlets_for_assignments(assignments, self.manager, self.baseUrl())

    def portlets_for_assignments(self, assignments, manager, base_url):
        category = self.__parent__.category
        key = self.__parent__.key

        data = []
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            if hasattr(assignments[idx], "__Broken_state__"):
                name = assignments[idx].__Broken_state__["__name__"]

            editview = queryMultiAdapter(
                (assignments[idx], self.request), name="edit", default=None
            )

            if editview is None:
                editviewName = ""
            else:
                editviewName = f"{base_url}/{name}/edit"

            portlet_hash = hashPortletInfo(
                dict(
                    manager=manager.__name__,
                    category=category,
                    key=key,
                    name=name,
                )
            )

            try:
                settings = IPortletAssignmentSettings(assignments[idx])
                visible = settings.get("visible", True)
            except TypeError:
                visible = False

            data.append(
                {
                    "title": assignments[idx].title,
                    "editview": editviewName,
                    "hash": portlet_hash,
                    "name": name,
                    "up_url": "%s/@@move-portlet-up" % (base_url),
                    "down_url": "%s/@@move-portlet-down" % (base_url),
                    "delete_url": "%s/@@delete-portlet" % (base_url),
                    "hide_url": "%s/@@toggle-visibility" % (base_url),
                    "show_url": "%s/@@toggle-visibility" % (base_url),
                    "visible": visible,
                }
            )
        if len(data) > 0:
            data[0]["up_url"] = data[-1]["down_url"] = None

        return data

    def addable_portlets(self):
        baseUrl = self.baseUrl()
        addviewbase = baseUrl.replace(self.context_url(), "")

        def sort_key(v):
            return v.get("title")

        def check_permission(p):
            addview = p.addview
            if not addview:
                return False

            addview = "{}/+/{}".format(
                addviewbase,
                addview,
            )
            if addview.startswith("/"):
                addview = addview[1:]
            try:
                self.context.restrictedTraverse(str(addview))
            except (AttributeError, KeyError, Unauthorized, NotFound):
                return False
            return True

        portlets = [
            {
                "title": p.title,
                "description": p.description,
                "addview": f"{addviewbase}/+/{p.addview}",
            }
            for p in self.manager.getAddablePortletTypes()
            if check_permission(p)
        ]

        portlets.sort(key=sort_key)
        return portlets

    @memoize
    def referer(self):
        view_name = self.request.get("viewname", None)
        key = self.request.get("key", None)
        base_url = self.request["ACTUAL_URL"]

        if view_name:
            base_url = self.context_url() + "/" + view_name

        if key:
            base_url += "?key=%s" % key

        return base_url

    @memoize
    def url_quote_referer(self):
        return url_quote(self.referer())

    @memoize
    def key(self):
        return self.request.get("key", None)

    # See note in plone.portlets.manager

    @memoize
    def _lazyLoadAssignments(self, manager):
        return self.__parent__.getAssignmentsForManager(manager)

    @memoize
    def context_url(self):
        return str(getMultiAdapter((self.context, self.request), name="absolute_url"))


@adapter(
    Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IPortletManager
)
class ContextualEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""

    template = ViewPageTemplateFile("templates/edit-manager-contextual.pt")

    def __init__(self, context, request, view, manager):
        EditPortletManagerRenderer.__init__(self, context, request, view, manager)

    def blacklist_status_action(self):
        baseUrl = str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        return baseUrl + "/@@set-portlet-blacklist-status"

    def manager_name(self):
        return self.manager.__name__

    def context_blacklist_status(self):
        assignable = getMultiAdapter(
            (
                self.context,
                self.manager,
            ),
            ILocalPortletAssignmentManager,
        )
        return assignable.getBlacklistStatus(CONTEXT_CATEGORY)

    def group_blacklist_status(self, check_parent=False):
        # If check_parent is True and the blacklist status is None, it returns the
        # parent status recursively.
        assignable = getMultiAdapter(
            (
                self.context,
                self.manager,
            ),
            ILocalPortletAssignmentManager,
        )
        status = assignable.getBlacklistStatus(GROUP_CATEGORY)

        if check_parent and status is None:
            # get status from parent recursively
            status = self.parent_blacklist_status(GROUP_CATEGORY)

        return status

    def content_type_blacklist_status(self, check_parent=False):
        assignable = getMultiAdapter(
            (
                self.context,
                self.manager,
            ),
            ILocalPortletAssignmentManager,
        )
        status = assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY)

        if check_parent and status is None:
            # get status from parent recursively
            status = self.parent_blacklist_status(CONTENT_TYPE_CATEGORY)

        return status

    def parent_blacklist_status(self, category):
        if IPortletContext.providedBy(self.context):
            pcontext = self.context
        else:
            pcontext = queryAdapter(self.context, IPortletContext)

        status = None

        current = pcontext.getParent()
        currentpc = pcontext
        while status is None and current is not None:
            assignable = getMultiAdapter(
                (
                    current,
                    self.manager,
                ),
                ILocalPortletAssignmentManager,
            )
            status = assignable.getBlacklistStatus(category)

            current = currentpc.getParent()
            if current is not None:
                if IPortletContext.providedBy(current):
                    currentpc = current
                else:
                    currentpc = queryAdapter(current, IPortletContext)
        return status

    def inherited_portlets(self):
        """Return the list of portlets inherited by the current context.

        Invisible (hidden) portlets are excluded.

        """
        context = aq_inner(self.context)

        data = []

        def is_visible(a):
            try:
                return IPortletAssignmentSettings(a).get("visible", True)
            except TypeError:
                # Assignment is broken
                return False

        while not IPloneSiteRoot.providedBy(context):
            if IAcquirer.providedBy(context):
                context = aq_parent(aq_inner(context))
            else:
                context = context.__parent__

            # we get the contextual portlets view to access its utility methods
            view = queryMultiAdapter(
                (context, self.request), name=self.__parent__.__name__
            )
            if view is not None:
                assignments = view.getAssignmentsForManager(self.manager)
                assignments_to_show = [a for a in assignments if is_visible(a)]
                base_url = view.getAssignmentMappingUrl(self.manager)
                data.extend(
                    self.portlets_for_assignments(
                        assignments_to_show, self.manager, base_url
                    )
                )

            assignable = queryMultiAdapter(
                (context, self.manager), ILocalPortletAssignmentManager
            )
            if assignable is not None and assignable.getBlacklistStatus(
                CONTEXT_CATEGORY
            ):
                # Current context has blocked inherited portlets, stop.
                break

        return data

    def global_portlets(self, category, prefix):
        """Return the list of global portlets from a given category for the current context.

        Invisible (hidden) portlets are excluded.

        """
        context = aq_inner(self.context)

        # get the portlet context
        pcontext = IPortletContext(self.context)

        portal_state = getMultiAdapter(
            (context, self.request), name="plone_portal_state"
        )
        base_url = portal_state.portal_url()

        portlets = []
        for cat, key in pcontext.globalPortletCategories(False):
            if cat == category:
                mapping = self.manager.get(category, None)
                assignments = []
                if mapping is not None:
                    is_visible = lambda a: IPortletAssignmentSettings(a).get(
                        "visible", True
                    )
                    assignments.extend(
                        [a for a in mapping.get(key, {}).values() if is_visible(a)]
                    )
                if assignments:
                    edit_url = "{}/++{}++{}+{}".format(
                        base_url,
                        prefix,
                        self.manager.__name__,
                        key,
                    )
                    portlets.extend(
                        self.portlets_for_assignments(
                            assignments, self.manager, edit_url
                        )
                    )

        return portlets

    def group_portlets(self):
        """Return the list of global portlets from the group category for the
        current context."""
        return self.global_portlets(GROUP_CATEGORY, "groupportlets")

    def content_type_portlets(self):
        """Return the list of global portlets from the content type category for
        the current context."""
        return self.global_portlets(CONTENT_TYPE_CATEGORY, "contenttypeportlets")


@adapter(Interface, IDefaultBrowserLayer, IManageDashboardPortletsView, IDashboard)
class DashboardEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for the dashboard"""


class ManagePortletAssignments(BrowserView):
    """Utility views for managing portlets for a particular column"""

    def authorize(self):
        authenticator = getMultiAdapter(
            (self.context, self.request), name="authenticator"
        )
        if not authenticator.verify():
            raise Unauthorized

    def _render_column(self):
        view_name = self.request.form.get("viewname")
        obj = aq_inner(self.context.__parent__)
        request = aq_inner(self.request)
        view = getMultiAdapter((obj, request), name=view_name)
        # view can have been customized TTW, see #11409
        if isinstance(view, TTWViewTemplateRenderer):
            view = view._getView()

        manager = getUtility(IPortletManager, name=self.context.__manager__)
        renderer = getMultiAdapter(
            (obj, request, view, manager), IPortletManagerRenderer
        )
        renderer.update()
        return renderer.__of__(obj).render()

    def finish_portlet_change(self):
        if self.request.form.get("ajax", False):
            return self._render_column()
        else:
            self.request.response.redirect(self._nextUrl())
            return ""

    # view @@move-portlet-up
    def move_portlet_up(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()

        keys = list(assignments.keys())

        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx - 1, name)
        assignments.updateOrder(keys)
        return self.finish_portlet_change()

    # view @@move-portlet-down
    def move_portlet_down(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()

        keys = list(assignments.keys())

        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx + 1, name)
        assignments.updateOrder(keys)
        return self.finish_portlet_change()

    # view @@delete-portlet
    def delete_portlet(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()

        # set fixing_up to True to let zope.container.contained
        # know that our object doesn't have __name__ and __parent__
        fixing_up = contained.fixing_up
        contained.fixing_up = True

        del assignments[name]

        # revert our fixing_up customization
        contained.fixing_up = fixing_up

        return self.finish_portlet_change()

    def _nextUrl(self):
        referer = self.request.get("referer")
        urltool = getToolByName(self.context, "portal_url")
        if referer:
            referer = url_unquote(referer)

        if not referer or not urltool.isURLInPortal(referer):
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name="absolute_url"))
            referer = f"{url}/@@manage-portlets"
        return referer

    def toggle_visibility(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        settings = IPortletAssignmentSettings(assignments[name])
        visible = settings.get("visible", True)
        settings["visible"] = not visible
        return self.finish_portlet_change()
