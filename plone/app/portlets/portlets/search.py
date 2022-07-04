from .. import PloneMessageFactory as _
from ..portlets import base
from plone.app.layout.navigation.root import getNavigationRoot
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implementer


class ISearchPortlet(IPortletDataProvider):
    """A portlet displaying a (live) search box"""

    enableLivesearch = schema.Bool(
        title=_("Enable LiveSearch"),
        description=_(
            "Enables the LiveSearch feature, which shows "
            "live results if the browser supports "
            "JavaScript."
        ),
        default=True,
        required=False,
    )


@implementer(ISearchPortlet)
class Assignment(base.Assignment):
    def __init__(self, enableLivesearch=True):
        self.enableLivesearch = enableLivesearch

    @property
    def title(self):
        return _("Search")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile("search.pt")
    action = "@@search"
    livesearch_action = "livesearch_reply"

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        portal_state = getMultiAdapter((context, request), name="plone_portal_state")
        self.navigation_root_url = portal_state.navigation_root_url()

    def enable_livesearch(self):
        return self.data.enableLivesearch

    def search_action(self):
        return f"{self.navigation_root_url}/{self.action}"

    def navigation_root_url(self):
        return getNavigationRoot(self.context)


class AddForm(base.AddForm):
    schema = ISearchPortlet
    label = _("Add Search Portlet")
    description = _("This portlet shows a search box.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    schema = ISearchPortlet
    label = _("Edit Search Portlet")
    description = _("This portlet shows a search box.")
