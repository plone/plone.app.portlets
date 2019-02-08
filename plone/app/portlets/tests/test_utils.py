# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.portlets.constants import USER_CATEGORY, CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.portlets import classic
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.utils import assignment_from_key


class TestAssignmentFromKey(PortletsTestCase):

    def afterSetUp(self):
        self.manager = getUtility(IPortletManager, name=u'plone.leftcolumn')
        self.cat = self.manager[USER_CATEGORY]
        self.cat[TEST_USER_ID] = PortletAssignmentMapping(manager=u'plone.leftcolumn',
                                                       category=USER_CATEGORY,
                                                       name=TEST_USER_ID)

    def testGetPortletFromContext(self):
        mapping = getMultiAdapter((self.portal, self.manager), IPortletAssignmentMapping)
        c = classic.Assignment()
        mapping['foo'] = c
        path = '/'.join(self.portal.getPhysicalPath())
        a = assignment_from_key(self.portal, u'plone.leftcolumn', CONTEXT_CATEGORY, path, 'foo')
        self.assertEqual(c, a)

    def testGetPortletFromContextUnicodePath(self):
        """Do not fail, if path is a unicode object.
        plone.portlets.utils.unhashPortletInfo returns a unicode path key.
        """
        mapping = getMultiAdapter((self.portal, self.manager), IPortletAssignmentMapping)
        c = classic.Assignment()
        mapping['foo'] = c
        path = u'/'.join(self.portal.getPhysicalPath())
        a = assignment_from_key(self.portal, u'plone.leftcolumn', CONTEXT_CATEGORY, path, 'foo')
        self.assertEqual(c, a)

    def testGetPortletFromUserCategory(self):
        c = classic.Assignment()
        self.cat[TEST_USER_ID]['foo'] = c
        a = assignment_from_key(self.portal, u'plone.leftcolumn', USER_CATEGORY, TEST_USER_ID, 'foo')
        self.assertEqual(c, a)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAssignmentFromKey))
    return suite
