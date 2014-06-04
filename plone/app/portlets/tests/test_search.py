from zope.component import getUtility, getMultiAdapter

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import search
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase


class TestSearchPortlet(PortletsTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Search')
        self.assertEquals(portlet.addview, 'portlets.Search')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Search')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(
            registered_interfaces,
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'])

    def testInterfaces(self):
        portlet = search.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Search')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], search.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = search.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, search.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = search.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, search.Renderer))


class TestRenderer(PortletsTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.app.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or search.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        view = self.renderer(self.portal)
        html = view.render()
        self.assertIn(
            'id="searchform"', html, 'Missing search form element')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSearchPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
