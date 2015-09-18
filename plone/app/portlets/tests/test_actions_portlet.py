from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import actions

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from Products.CMFCore.utils import getToolByName


class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='portlets.Actions')
        self.assertEquals(portlet.addview,
                          'portlets.Actions')
        return

    def test_interfaces(self):
        portlet = actions.Assignment(ptitle=u'actions', category=u'document', show_icons=True)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))
        return

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='portlets.Actions')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        data = {
            'ptitle': u"Actions",
            'category': u'document',
            'show_icons': True}
        addview.createAndAdd(data=data)

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   actions.Assignment))
        return

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = actions.Assignment(ptitle=u'actions', category=u'document', show_icons=True)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, actions.EditForm))
        return

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = actions.Assignment(ptitle=u'actions', category=u'document', show_icons=True)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, actions.Renderer))
        return


class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or actions.Assignment(ptitle=u'actions', category=u'site_actions', show_icons=True)
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        migtool = getToolByName(self.portal, 'portal_migration')

        r = self.renderer(context=self.portal,
                          assignment=actions.Assignment(ptitle=u'actions', category=u'site_actions', show_icons=True))
        r = r.__of__(self.folder)
        r.update()
        output = r.actionLinks()

        if int(migtool.getInstanceVersion()[0]) >= 4:
            self.failUnlessEqual(len(output), 3)
        else:
            self.failUnlessEqual(len(output), 4)

        first = output[0]
        self.failUnlessEqual(first['url'], 'http://nohost/plone/sitemap')
#        self.failUnless(first['icon'] is not None, "We should have an icon")
        self.failUnlessEqual(first['title'], u"Site Map")

        return

    def test_render_woicon(self):
        """Without icons"""
        r = self.renderer(
            context=self.portal,
            assignment=actions.Assignment(
                ptitle=u'actions', category=u'site_actions', show_icons=False))
        r = r.__of__(self.folder)
        r.update()
        output = r.actionLinks()
        first = output[0]
        self.failUnless(first['icon'] is None, "We should not have an icon")
        return

    def test_multiple_portlets(self):
        """This test ensures that we can add more than one action portlet on
        the same page with different action categories and show_icons option
        and those portlets will work as they are intended to work.

        This test was written due to bug caused by caching actionLinks portlet
        renderer's method
        """
        migtool = getToolByName(self.portal, 'portal_migration')

        # let's create two different portlet renderers for the same context
        # thus for the same REQUEST, plone memoize uses REQUEST to cache data
        r1 = self.renderer(assignment=actions.Assignment(
            ptitle=u'tabs', category=u'portal_tabs', show_icons=True))
        r1 = r1.__of__(self.folder)
        r1.update()
        links1 = r1.actionLinks()
        r2 = self.renderer(assignment=actions.Assignment(ptitle=u'site actions', category=u'site_actions', show_icons=False))
        r2 = r2.__of__(self.folder)
        r2.update()
        links2 = r2.actionLinks()

        # check the portal_tabs links (portal_tabs is somehow special)
        self.assertEquals(len(links1), 5)
        self.assertEquals(links1[0]['title'], u'Home')

        # now check the site_actions links
        # this was failing until the caching of actionLinks method was fixed
        if int(migtool.getInstanceVersion()[0]) >= 4:
            self.assertEquals(len(links2), 3)
        else:
            self.assertEquals(len(links2), 4)
        self.assertEquals(links2[0]['title'], u'Site Map')
        self.assertEquals(links2[0]['url'], 'http://nohost/plone/sitemap')
        self.assertEquals(links2[0]['icon'], None)
        return

    def test_portal_tabs(self):
        """Special stuff for the portal_tabs category which actions rely on
        content in Plone content root
        """
        r = self.renderer(
            context=self.portal,
            assignment=actions.Assignment(
                ptitle=u'actions', category=u'portal_tabs', show_icons=True))
        r = r.__of__(self.folder)
        r.update()
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = set([u'Test Folder', u'Home', u'Users', u'News', u'Events'])
        got = set([unicode(link['title']) for link in output])
        self.failUnlessEqual(got, expected)
        return

    def test_object_buttons(self):
        """Special stuff for the object_buttons category
        """
        r = self.renderer(
            context=self.portal['news'],
            assignment=actions.Assignment(
                ptitle=u'actions', category=u'object_buttons', show_icons=False))
        r = r.__of__(self.folder)
        r.update()
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = set([u'Cut', u'Copy', u'Rename', u'Delete'])
        got = set([unicode(link['title']) for link in output])
        self.failUnlessEqual(got, expected)
        return

    def test_object_buttons_with_icons(self):
        """Special stuff for the object_buttons category (bug in render_icons)
"""
        r = self.renderer(
            context=self.portal['news'],
            assignment=actions.Assignment(
                ptitle=u'actions', category=u'object_buttons', show_icons=True))
        r = r.__of__(self.folder)
        r.update()
        self.failUnless(r.actionLinks)
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = set([u'Cut', u'Copy', u'Rename', u'Delete'])
        got = set([unicode(link['title']) for link in output])
        self.failUnlessEqual(got, expected)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
