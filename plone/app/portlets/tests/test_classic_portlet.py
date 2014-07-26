from zope.component import getUtility, getMultiAdapter
from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import classic

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Classic')
        self.assertEqual(portlet.addview, 'portlets.Classic')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Classic')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = classic.Assignment(template='portlet_recent', macro='portlet')
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Classic')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], classic.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = classic.Assignment(template='portlet_recent', macro='portlet')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, classic.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = classic.Assignment(template='portlet_recent', macro='portlet')

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, classic.Renderer))


class TestRenderer(PortletsTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or classic.Assignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testUseMacro(self):
        r = self.renderer(assignment=classic.Assignment(template='portlet_recent', macro='portlet'))
        self.assertEqual(True, r.use_macro())
        r = self.renderer(assignment=classic.Assignment(template='portlet_recent', macro=None))
        self.assertEqual(False, r.use_macro())

    def testPathExpression(self):
        r = self.renderer(assignment=classic.Assignment(template='portlet_recent', macro='portlet'))
        self.assertEqual('context/portlet_recent/macros/portlet', r.path_expression())
        r = self.renderer(assignment=classic.Assignment(template='portlet_recent', macro=None))
        self.assertEqual('context/portlet_recent', r.path_expression())

    def testRenderClassicPortlet(self):
        r = self.renderer(assignment=classic.Assignment(template='base_view', macro='content-core'))
        r.render()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
