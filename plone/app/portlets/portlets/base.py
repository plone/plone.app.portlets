from ..browser.formhelper import AddForm
from ..browser.formhelper import EditForm
from ..browser.formhelper import NullAddForm
from OFS.SimpleItem import SimpleItem
from plone.app.portlets.interfaces import IDeferredPortletRenderer
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.container.contained import Contained
from zope.interface import implementer


@implementer(IPortletAssignment)
class Assignment(SimpleItem, Contained):
    """Base class for assignments.

    Your type may override the 'title', 'available' and 'data' properties, and
    may
    """

    __name__ = ""

    @property
    def id(self):
        return getattr(self, "__name__", "")

    @property
    def title(self):
        return self.id

    def available(self, context, request):
        """By default, this portlet is always available"""
        return True

    @property
    def data(self):
        """Make the assignment itself represent the data object that is being rendered."""
        return self


@implementer(IPortletRenderer)
class Renderer:
    """Base class for portlet renderers.

    You must override render() to return a string to render. One way of
    doing this is to write:

        from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
        ...
        render = ViewPageTemplateFile('mytemplate.pt')

    This will render the template mytemplate.pt, found in the same directory
    as your source code file.
    """

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view
        self.manager = manager
        self.data = data

    def update(self):
        pass

    def render(self):
        raise NotImplementedError(
            "You must implement 'render' as a method " "or page template file attribute"
        )

    @property
    def available(self):
        """By default, portlets are available"""
        return True


@implementer(IDeferredPortletRenderer)
class DeferredRenderer(Renderer):
    """provide defer functionality via KSS

    in here don't override render() but instead override render_full

    """

    render_preload = ViewPageTemplateFile("deferred_portlet.pt")

    def render_full(self):
        raise NotImplemented(
            "You must implement 'render_full' as a method or page template file attribute"
        )

    def render(self):
        """render the portlet

        the template gets choosen depending on the initialize state
        """
        if self.initializing:
            return self.render_preload()
        else:
            return self.render_full()
