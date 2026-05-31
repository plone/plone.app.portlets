Introduction
=============

plone.app.portlets provides a Plone-specific user interface for
plone.portlets, as well as a standard set of portlets that ship with Plone.


Call one portlet by URL
=======================

To call a portlet by its URL, for example, to update it via an AJAX call, use
the `@@render-portlet` view in your portlet renderer with `portlethash` as a
query parameter.

The following example shows how to construct a reload URL for a portlet::

    from plone.app.portlets.portlets.base import Renderer
    from Products.CMFPlone.utils import safe_unicode


    class BasePortletRenderer(Renderer):
        @property
        def hash(self):
            portlethash = self.request.form.get(
                "portlethash", getattr(self, "__portlet_metadata__", {}).get("hash", "")
            )
            return portlethash

        @property
        def reload_url(self):
            base_url = self.context.absolute_url()
            hash = safe_unicode(self.hash)
            return f"{base_url}/@@render-portlet?portlethash={hash}"


Compatibility
=============

plone.app.portlets 2.4.x is for Plone 4.3.
plone.app.portlets 2.5.x is for Plone 4.3 with plone.app.event (makes the calendar- and events-portlets use the p.a.event implementation)
plone.app.portlets 3.x is for Plone 5.0
plone.app.portlets 4.x is for Plone 5.1 and 5.2.
plone.app.portlets 5.x is for Plone 6.0.
