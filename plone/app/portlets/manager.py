from .interfaces import IColumn
from .interfaces import IDashboard
from Acquisition import aq_acquire
from Acquisition import aq_inner
from Acquisition import Explicit
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.manager import PortletManagerRenderer as BasePortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import logging
import sys


logger = logging.getLogger("portlets")


class PortletManagerRenderer(BasePortletManagerRenderer, Explicit):
    """A Zope 2 implementation of the default PortletManagerRenderer"""

    def _dataToPortlet(self, data):
        """Helper method to get the correct IPortletRenderer for the given
        data object.
        """
        portlet = getMultiAdapter(
            (
                self.context,
                self.request,
                self.__parent__,
                self.manager,
                data,
            ),
            IPortletRenderer,
        )
        return portlet


@adapter(Interface, IDefaultBrowserLayer, IBrowserView, IColumn)
class ColumnPortletManagerRenderer(PortletManagerRenderer):
    """A renderer for the column portlets"""

    template = ViewPageTemplateFile("browser/templates/column.pt")
    error_message = ViewPageTemplateFile("browser/templates/error_message.pt")

    def _context(self):
        return aq_inner(self.context)

    def base_url(self):
        """If context is a default-page, return URL of folder, else
        return URL of context.
        """
        return str(
            getMultiAdapter(
                (
                    self._context(),
                    self.request,
                ),
                name="absolute_url",
            )
        )

    def safe_render(self, portlet_renderer):
        try:
            return portlet_renderer.render()
        except ConflictError:
            raise
        except Exception:
            logger.exception("Error while rendering %r" % self)
            aq_acquire(self, "error_log").raising(sys.exc_info())
            return self.error_message()


@adapter(Interface, IDefaultBrowserLayer, IBrowserView, IDashboard)
class DashboardPortletManagerRenderer(ColumnPortletManagerRenderer):
    """Render a column of the dashboard"""

    template = ViewPageTemplateFile("browser/templates/dashboard-column.pt")
