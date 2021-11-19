from ..interfaces import IPortletPermissionChecker
from .interfaces import IPortletAdding
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from warnings import warn
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.interface import implementer


@implementer(IPortletAdding)
class PortletAdding(SimpleItem, BrowserView):

    context = None
    request = None

    # This is necessary so that context.absolute_url() works properly on the
    # add form, which in turn fixes the <base /> URL
    id = "+"

    def add(self, content):
        """Add the rule to the context"""
        context = aq_inner(self.context)
        manager = aq_base(context)

        IPortletPermissionChecker(context)()

        chooser = INameChooser(manager)
        manager[chooser.chooseName(None, content)] = content

    @property
    def referer(self):
        return self.request.get("referer", "")

    def nextURL(self):
        urltool = getToolByName(self.context, "portal_url")
        referer = self.referer
        if not referer or not urltool.isURLInPortal(referer):
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name="absolute_url"))
            referer = url + "/@@manage-portlets"
        return referer

    def renderAddButton(self):
        warn(
            "The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning,
            2,
        )

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

    @property
    def contentName(self):
        return None

    def addingInfo():
        return None

    def isSingleMenuItem():
        return False

    def hasCustomAddView():
        return 0
