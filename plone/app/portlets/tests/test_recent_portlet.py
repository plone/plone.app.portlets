from zope.component import getUtility, getMultiAdapter

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import recent
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Recent')
        self.assertEqual(portlet.addview, 'portlets.Recent')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Recent')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = recent.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Recent')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], recent.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = recent.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, recent.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = recent.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, recent.Renderer))


class TestRenderer(PortletsTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.app.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or recent.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_recent_items(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        if 'news' in self.portal:
            self.portal._delObject('news')
        if 'events' in self.portal:
            self.portal._delObject('events')
        if 'front-page' in self.portal:
            self.portal._delObject('front-page')
        if 'Members' in self.portal:
            self.portal._delObject('Members')
            self.folder = None
        if 'folder' in self.portal:
            self.portal._delObject('folder')
        if 'users' in self.portal:
            self.portal._delObject('users')
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        r = self.renderer(assignment=recent.Assignment())
        self.assertEqual(2, len(r.recent_items()))

        r = self.renderer(assignment=recent.Assignment(count=1))
        self.assertEqual(1, len(r.recent_items()))

    def test_recently_modified_link(self):
        r = self.renderer(assignment=recent.Assignment())
        self.assertTrue(r.recently_modified_link().endswith('/recently_modified'))

    def test_title(self):
        r = self.renderer(assignment=recent.Assignment())
        self.assertEqual(str(r.title), 'box_recent_changes')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
