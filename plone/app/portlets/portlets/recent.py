# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
import os

class IRecentPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5,
                       min=1)

    no_icons = schema.Bool(
        title=_(u"Suppress Icons "),
        description=_(
            u"If enabled, the portlet will not show document type icons"),
        required=True,
        default=False)

    ov_thumbsize = schema.TextLine(
        title=_(u"Override thumb size "),
        description=_(u"<br><ul><li> Enter a valid scale name"
             u"(see 'Image Handling' control panel) to override"
             u" e.g. icon, tile, thumb, mini, preview, ... )  </li>"
             u"<li>leave empty to use default "
             u"(see 'Site' control panel)</li></ul>"),
        required=False,
        default=u'')

    no_thumbs = schema.Bool(
        title=_(u"Suppress thumbs "),
        description=_(
            u"If enabled, the portlet will not show thumbs"),
        required=True,
        default=False)

@implementer(IRecentPortlet)
class Assignment(base.Assignment):
    no_icons = False
    ov_thumbsize = ''

    def __init__(self, count=5, no_icons=False,
                ov_thumbsize=u'', no_thumbs=False):
        self.count = count
        self.no_icons = no_icons
        self.ov_thumbsize = ov_thumbsize
        self.no_thumbs = no_thumbs

    @property
    def title(self):
        return _(u"Recent items")


def _render_cachekey(fun, self):
    if self.anonymous:
        raise ram.DontCache()
    return render_cachekey(fun, self)


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('recent.pt')

    title = _('box_recent_changes', default=u"Recent Changes")

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request), name='plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.navigation_root_url = portal_state.navigation_root_url()
        self.typesToShow = portal_state.friendly_types()
        self.navigation_root_path = portal_state.navigation_root_path()

        plone_tools = getMultiAdapter(
            (context, self.request), name='plone_tools')
        self.catalog = plone_tools.catalog()

    ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return not self.anonymous and self.data.count > 0 and len(self._data())

    def recent_items(self):
        return self._data()

    def recently_modified_link(self):
        return '%s/recently_modified' % self.navigation_root_url

    @memoize
    def _data(self):
        limit = self.data.count
        path = self.navigation_root_path
        return self.catalog(portal_type=self.typesToShow,
                            path=path,
                            sort_on='modified',
                            sort_order='reverse',
                            sort_limit=limit)[:limit]

    @memoize
    def thumb_size(self):
        ''' use  overrride value or read thumb_size from registry
            image sizes must fit to value in allowed image sizes
            none from both sources will suppress thumb!
        '''
        if getattr(self.data,'no_thumbs',False):
            #individual setting overrides ...
            return 'none'
        thsize=getattr(self.data,'ov_thumbsize','')
        if thsize > ' ':
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        thumb_size_portlet = settings.thumb_size_portlet
        return thumb_size_portlet

    def getMimeTypeIcon(self,obj):
        fileo = obj.getObject().file
        portal_url = getNavigationRoot(self.context)
        mtt = getToolByName(self.context,'mimetypes_registry')
        if fileo.contentType:
            ctype = mtt.lookup(fileo.contentType)
            return os.path.join(portal_url,
                 guess_icon_path(ctype[0])
                )
        return None 

class AddForm(base.AddForm):
    schema = IRecentPortlet
    label = _(u"Add Recent Portlet")
    description = _(u"This portlet displays recently modified content.")

    def create(self, data):
        return Assignment(count=data.get('count', 5))


class EditForm(base.EditForm):
    schema = IRecentPortlet
    label = _(u"Edit Recent Portlet")
    description = _(u"This portlet displays recently modified content.")
