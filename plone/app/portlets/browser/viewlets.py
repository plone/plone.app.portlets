from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from datetime import date


class ManagePortletsFallbackViewlet(ViewletBase):
    """Manage portlets fallback link that sits below content"""

    index = ViewPageTemplateFile("templates/manage_portlets_fallback.pt")

    def update(self):
        plonelayout = getMultiAdapter(
            (self.context, self.request), name=u"plone_layout"
        )
        context_state = getMultiAdapter(
            (self.context, self.request), name=u"plone_context_state"
        )

        self.portlet_assignable = context_state.portlet_assignable()
        self.sl = plonelayout.have_portlets("plone.leftcolumn", self.context)
        self.sr = plonelayout.have_portlets("plone.rightcolumn", self.context)
        self.object_url = context_state.object_url()

    def available(self):
        secman = getSecurityManager()
        has_manage_portlets_permission = secman.checkPermission(
            "Portlets: Manage portlets", self.context
        )
        if not has_manage_portlets_permission:
            return False
        return bool(not self.sl and not self.sr and self.portlet_assignable)

class FooterViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/footer.pt")

    def update(self):
        super(FooterViewlet, self).update()
        self.year = date.today().year

    def render_footer_portlets(self):
        """
        You might ask, why is this necessary. Well, let me tell you a story...

        plone.app.portlets, in order to provide @@manage-portlets on a context,
        overrides the IPortletRenderer for the IManageContextualPortletsView
        view.
        See plone.portlets and plone.app.portlets

        Seems fine right? Well, most of the time it is. Except, here.
        Previously, we were just using the syntax like
        `provider:plone.footerportlets` to render the footer portlets.
        Since this tal expression was inside a viewlet,
        the view is no longer IManageContextualPortletsView when
        visiting @@manage-portlets. Instead, it was IViewlet.
        See zope.contentprovider

        In to fix this short coming, we render the portlet column by
        manually doing the multi adapter lookup and then manually
        doing the rendering for the content provider.
        See zope.contentprovider
        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name="plone.footerportlets"
        )
        portlet_manager.update()
        return portlet_manager.render()
