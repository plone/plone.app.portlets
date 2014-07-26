from Acquisition import aq_base
from Acquisition import aq_parent
from AccessControl import Unauthorized

from Testing.ZopeTestCase import user_name

from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.portlets import classic
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestTraversal(PortletsTestCase):

    def _assertSameObject(self, a, b):
        self.assertTrue(aq_base(a) is aq_base(b))

    def testContextNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.folder.restrictedTraverse('++contextportlets++plone.leftcolumn')
        self._assertSameObject(aq_parent(mapping), self.folder)
        mapping['foo'] = assignment
        target = getMultiAdapter((self.folder, manager), IPortletAssignmentMapping)
        self._assertSameObject(target['foo'], assignment)
        self.assertEqual('++contextportlets++plone.leftcolumn', mapping.id)

    def testDashboardNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++dashboard++plone.dashboard1+' + user_name)
        self._assertSameObject(aq_parent(mapping), self.portal)
        mapping['foo'] = assignment
        self._assertSameObject(manager[USER_CATEGORY][user_name]['foo'], assignment)
        self.assertEqual('++dashboard++plone.dashboard1+' + user_name, mapping.id)

    def testGroupDashboardNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++groupdashboard++plone.dashboard1+Reviewers')
        self._assertSameObject(aq_parent(mapping), self.portal)
        mapping['foo'] = assignment
        self._assertSameObject(manager[GROUP_CATEGORY]['Reviewers']['foo'], assignment)
        self.assertEqual('++groupdashboard++plone.dashboard1+Reviewers', mapping.id)

    def testGroupDashboardNamespaceChecker(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++groupdashboard++plone.dashboard1+Reviewers')

        checker = IPortletPermissionChecker(mapping)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        checker() # no exception

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized, checker)

    def testGroupNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.portal.restrictedTraverse('++groupportlets++plone.leftcolumn+Reviewers')
        self._assertSameObject(aq_parent(mapping), self.portal)
        mapping['foo'] = assignment
        self._assertSameObject(manager[GROUP_CATEGORY]['Reviewers']['foo'], assignment)
        self.assertEqual('++groupportlets++plone.leftcolumn+Reviewers', mapping.id)

    def testContentTypeNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.portal.restrictedTraverse('++contenttypeportlets++plone.leftcolumn+Image')
        self._assertSameObject(aq_parent(mapping), self.portal)
        mapping['foo'] = assignment
        self._assertSameObject(manager[CONTENT_TYPE_CATEGORY]['Image']['foo'], assignment)
        self.assertEqual('++contenttypeportlets++plone.leftcolumn+Image', mapping.id)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTraversal))
    return suite
