from .. import PloneMessageFactory as _
from ..portlets import base
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.base.defaultpage import is_default_page
from plone.base.interfaces import INavigationSchema
from plone.base.interfaces import INonStructuralFolder
from plone.base.interfaces import ISiteSchema
from plone.base.utils import safe_callable
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.utils import typesToList
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from zExceptions import NotFound
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface

import os


class INavigationPortlet(IPortletDataProvider):
    """A portlet which can render the navigation tree"""

    name = schema.TextLine(
        title=_("label_navigation_title", default="Title"),
        description=_(
            "help_navigation_title", default="The title of the navigation tree."
        ),
        default="",
        required=False,
    )

    root_uid = schema.Choice(
        title=_("label_navigation_root_path", default="Root node"),
        description=_(
            "help_navigation_root",
            default="You may search for and choose a folder "
            "to act as the root of the navigation tree. "
            "Leave blank to use the Plone site root.",
        ),
        required=False,
        source=CatalogSource(is_folderish=True),
    )

    includeTop = schema.Bool(
        title=_("label_include_top_node", default="Include top node"),
        description=_(
            "help_include_top_node",
            default="Whether or not to show the top, or 'root', "
            "node in the navigation tree. This is affected "
            "by the 'Start level' setting.",
        ),
        default=False,
        required=False,
    )

    currentFolderOnly = schema.Bool(
        title=_(
            "label_current_folder_only",
            default="Only show the contents of the current folder.",
        ),
        description=_(
            "help_current_folder_only",
            default="If selected, the navigation tree will "
            "only show the current folder and its "
            "children at all times.",
        ),
        default=False,
        required=False,
    )

    topLevel = schema.Int(
        title=_("label_navigation_startlevel", default="Start level"),
        description=_(
            "help_navigation_start_level",
            default="An integer value that specifies the number of folder "
            "levels below the site root that must be exceeded "
            "before the navigation tree will display. 0 means "
            "that the navigation tree should be displayed "
            "everywhere including pages in the root of the site. "
            "1 means the tree only shows up inside folders "
            "located in the root and downwards, never showing "
            "at the top level.",
        ),
        default=1,
        required=False,
    )

    bottomLevel = schema.Int(
        title=_("label_navigation_tree_depth", default="Navigation tree depth"),
        description=_(
            "help_navigation_tree_depth",
            default="How many folders should be included "
            "before the navigation tree stops. 0 "
            "means no limit. 1 only includes the "
            "root folder.",
        ),
        default=0,
        required=False,
    )

    no_icons = schema.Bool(
        title=_("Suppress Icons"),
        description=_("If enabled, the portlet will not show document type icons."),
        required=False,
        default=False,
    )

    thumb_scale = schema.TextLine(
        title=_("Override thumb scale"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    no_thumbs = schema.Bool(
        title=_("Suppress thumbs"),
        description=_("If enabled, the portlet will not show thumbs."),
        required=False,
        default=False,
    )


@implementer(INavigationPortlet)
class Assignment(base.Assignment):

    name = ""
    root = None
    root_uid = None
    currentFolderOnly = False
    includeTop = False
    topLevel = 1
    bottomLevel = 0
    no_icons = False
    thumb_scale = None
    no_thumbs = False

    def __init__(
        self,
        name="",
        root_uid=None,
        currentFolderOnly=False,
        includeTop=False,
        topLevel=1,
        bottomLevel=0,
        no_icons=False,
        thumb_scale=None,
        no_thumbs=False,
    ):
        self.name = name
        self.root_uid = root_uid
        self.currentFolderOnly = currentFolderOnly
        self.includeTop = includeTop
        self.topLevel = topLevel
        self.bottomLevel = bottomLevel
        self.no_icons = no_icons
        self.thumb_scale = thumb_scale
        self.no_thumbs = no_thumbs

    @property
    def title(self):
        """
        Display the name in portlet mngmt interface
        """
        if self.name:
            return self.name
        return _("Navigation")

    def _root(self):
        # This is only called if the instance doesn't have a root_uid
        # attribute, which is probably because it has an old 'root'
        # attribute that needs to be converted.
        root = self.root
        if not root:
            return None
        portal = getToolByName(self, "portal_url").getPortalObject()
        navroot = getNavigationRootObject(self, portal)
        try:
            root = navroot.unrestrictedTraverse(root.lstrip("/"))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return root.UID()

    root_uid = ComputedAttribute(_root, 1)


class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.urltool = getToolByName(context, "portal_url")

    def title(self):
        return self.data.name or self.data.title

    def hasName(self):
        return self.data.name

    @property
    def available(self):
        rootpath = self.getNavRootPath()
        if rootpath is None:
            return False

        if self.data.bottomLevel < 0:
            return True

        tree = self.getNavTree()
        return len(tree["children"]) > 0

    def include_top(self):
        return getattr(self.data, "includeTop", True)

    def navigation_root(self):
        return self.getNavRoot()

    def heading_link_target(self):
        """
        Get the href target where clicking the portlet header will take you.

        If this is a customized portlet with a custom root item set,
        we probably want to take the user to the custom root item instead
        of the sitemap of the navigation root.

        Plone does not have subsection sitemaps so there is no point of
        displaying /sitemap links for anything besides nav root.
        """

        if not self.data.root_uid and not self.data.currentFolderOnly:
            # No particular root item assigned -> should get link to the
            # navigation root sitemap of the current context acquisition chain
            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            )
            return portal_state.navigation_root_url() + "/sitemap"

        nav_root = self.getNavRoot()

        # Root content item gone away or similar issue
        if not nav_root:
            return None

        if INavigationRoot.providedBy(nav_root) or ISiteRoot.providedBy(nav_root):
            # For top level folders go to the sitemap
            return nav_root.absolute_url() + "/sitemap"
        else:
            # Go to the item /view we have chosen as root item
            return nav_root.absolute_url()

    def root_type_name(self):
        root = self.getNavRoot()
        return queryUtility(IIDNormalizer).normalize(root.portal_type)

    def root_item_class(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        container = aq_parent(context)
        if aq_base(root) is aq_base(context) or (
            aq_base(root) is aq_base(container) and is_default_page(container, context)
        ):
            return "navTreeCurrentItem"
        return ""

    def root_is_portal(self):
        root = self.getNavRoot()
        return aq_base(root) is aq_base(self.urltool.getPortalObject())

    def createNavTree(self):
        data = self.getNavTree()

        bottomLevel = self.data.bottomLevel or 0

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=1, bottomLevel=bottomLevel)
        else:
            return self.recurse(
                children=data.get("children", []), level=1, bottomLevel=bottomLevel
            )

    # Cached lookups

    @memoize
    def getNavRootPath(self):
        return getRootPath(
            self.context,
            self.data.currentFolderOnly,
            self.data.topLevel,
            self.data.root_uid,
        )

    @memoize
    def getNavRoot(self, _marker=None):
        if _marker is None:
            _marker = []
        portal = self.urltool.getPortalObject()
        rootPath = self.getNavRootPath()
        if rootPath is None:
            return None

        if rootPath == self.urltool.getPortalPath():
            return portal
        else:
            try:
                return portal.unrestrictedTraverse(rootPath)
            except (AttributeError, KeyError, TypeError, NotFound):
                # TypeError: object is unsubscribtable might be
                # risen in some cases
                return portal

    @memoize
    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(
            context, obj=context, query=queryBuilder(), strategy=strategy
        )

    _template = ViewPageTemplateFile("navigation.pt")
    recurse = ViewPageTemplateFile("navigation_recurse.pt")

    @memoize
    def thumb_scale(self):
        """Use override value or read thumb_scale from registry.
        Image sizes must fit to value in allowed image sizes.
        None will suppress thumb.
        """
        if getattr(self.data, "no_thumbs", False):
            # Individual setting overrides
            return None
        thsize = getattr(self.data, "thumb_scale", None)
        if thsize:
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        if settings.no_thumbs_portlet:
            return "none"
        thumb_scale_portlet = settings.thumb_scale_portlet
        return thumb_scale_portlet

    def update(self):
        pass

    def render(self):
        return self._template()


class AddForm(base.AddForm):
    schema = INavigationPortlet
    label = _("Add Navigation Portlet")
    description = _("This portlet displays a navigation tree.")

    def create(self, data):
        return Assignment(
            name=data.get("name", ""),
            root_uid=data.get("root_uid", ""),
            currentFolderOnly=data.get("currentFolderOnly", False),
            includeTop=data.get("includeTop", False),
            topLevel=data.get("topLevel", 0),
            bottomLevel=data.get("bottomLevel", 0),
        )


class EditForm(base.EditForm):
    schema = INavigationPortlet
    label = _("Edit Navigation Portlet")
    description = _("This portlet displays a navigation tree.")


@implementer(INavigationQueryBuilder)
@adapter(Interface, INavigationPortlet)
class QueryBuilder:
    """Build a navtree query based on the settings in INavigationSchema
    and those set on the portlet.
    """

    def __init__(self, context, portlet):
        self.context = context
        self.portlet = portlet

        portal_properties = getToolByName(context, "portal_properties")
        navtree_properties = getattr(portal_properties, "navtree_properties")

        # Acquire a custom nav query if available
        customQuery = getattr(context, "getCustomNavQuery", None)
        if customQuery is not None and safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query
        root = uuidToObject(portlet.root_uid)
        if root is not None:
            rootPath = "/".join(root.getPhysicalPath())
        else:
            rootPath = getNavigationRoot(context)
        currentPath = "/".join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if currentPath != rootPath and not currentPath.startswith(rootPath + "/"):
            query["path"] = {"query": rootPath, "depth": 1}
        else:
            query["path"] = {"query": currentPath, "navtree": 1}

        topLevel = portlet.topLevel
        if topLevel and topLevel > 0:
            query["path"]["navtree_start"] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query["portal_type"] = typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty("sortAttribute", None)
        if sortAttribute is not None:
            query["sort_on"] = sortAttribute
            sortOrder = navtree_properties.getProperty("sortOrder", None)
            if sortOrder is not None:
                query["sort_order"] = sortOrder

        # Filter on workflow states, if enabled
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(INavigationSchema, prefix="plone")
        if navigation_settings.filter_on_workflow:
            query["review_state"] = navigation_settings.workflow_states_to_show

        self.query = query

    def __call__(self):
        return self.query


@implementer(INavtreeStrategy)
@adapter(Interface, INavigationPortlet)
class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet"""

    def __init__(self, context, portlet):
        SitemapNavtreeStrategy.__init__(self, context, portlet)

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = portlet.bottomLevel or 0

        self.rootPath = getRootPath(
            context, portlet.currentFolderOnly, portlet.topLevel, portlet.root_uid
        )

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        depth = node.get("depth", 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True


def getRootPath(context, currentFolderOnly, topLevel, root):
    """Helper function to calculate the real root path"""
    context = aq_inner(context)
    if currentFolderOnly:
        folderish = getattr(
            aq_base(context), "isPrincipiaFolderish", False
        ) and not INonStructuralFolder.providedBy(context)
        parent = aq_parent(context)

        is_default_page = False
        browser_default = IBrowserDefault(parent, None)
        if browser_default is not None:
            is_default_page = browser_default.getDefaultPage() == context.getId()

        if not folderish or is_default_page:
            return "/".join(parent.getPhysicalPath())
        else:
            return "/".join(context.getPhysicalPath())

    root = uuidToObject(root)
    if root is not None:
        rootPath = "/".join(root.getPhysicalPath())
    else:
        rootPath = getNavigationRoot(context)

    # Adjust for topLevel
    if topLevel > 0:
        contextPath = "/".join(context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath) + 1 :]
        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split("/")
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath + "/" + "/".join(contextSubPathElements[:topLevel])
        else:
            return None

    return rootPath
