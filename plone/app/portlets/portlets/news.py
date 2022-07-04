from .. import PloneMessageFactory as _
from ..cache import render_cachekey
from ..portlets import base
from Acquisition import aq_inner
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform.directives import widget
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer


class INewsPortlet(IPortletDataProvider):

    count = schema.Int(
        title=_("Number of items to display"),
        description=_("How many items to list."),
        required=True,
        default=5,
        min=1,
    )

    widget(state=SelectFieldWidget)
    state = schema.Tuple(
        title=_("Workflow state"),
        description=_("Items in which workflow state to show."),
        default=("published",),
        required=False,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowStates"),
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
        description=_("If enabled, the portlet will not show thumbs"),
        required=False,
        default=False,
    )


@implementer(INewsPortlet)
class Assignment(base.Assignment):

    thumb_scale = None
    no_thumbs = False

    def __init__(
        self, count=5, state=("published",), thumb_scale=None, no_thumbs=False
    ):
        self.count = count
        self.state = state
        self.thumb_scale = thumb_scale
        self.no_thumbs = no_thumbs

    @property
    def title(self):
        return _("News")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile("news.pt")

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def published_news_items(self):
        return self._data()

    def all_news_link(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request), name="plone_portal_state"
        )
        portal = portal_state.portal()
        if "news" in getNavigationRootObject(context, portal).objectIds():
            return "%s/news" % portal_state.navigation_root_url()
        return None

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, "portal_catalog")
        portal_state = getMultiAdapter(
            (context, self.request), name="plone_portal_state"
        )
        path = portal_state.navigation_root_path()
        limit = self.data.count
        state = self.data.state
        return catalog(
            portal_type="News Item",
            review_state=state,
            path=path,
            sort_on="Date",
            sort_order="reverse",
            sort_limit=limit,
        )[:limit]

    def thumb_scale(self):
        """Use override value or read thumb_scale from registry.
        Image sizes must fit to value in allowed image sizes.
        None will suppress thumb.
        """
        if getattr(self.data, "no_thumbs", False):
            # Individual setting overrides ...
            return None
        thsize = getattr(self.data, "thumb_scale", "")
        if thsize:
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        if settings.no_thumbs_portlet:
            return None
        thumb_scale_portlet = settings.thumb_scale_portlet
        return thumb_scale_portlet


class AddForm(base.AddForm):
    schema = INewsPortlet
    label = _("Add News Portlet")
    description = _("This portlet displays recent News Items.")

    def create(self, data):
        return Assignment(
            count=data.get("count", 5),
            state=data.get("state", ("published",)),
        )


class EditForm(base.EditForm):
    schema = INewsPortlet
    label = _("Edit News Portlet")
    description = _("This portlet displays recent News Items.")
