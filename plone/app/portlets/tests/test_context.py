from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles

from plone.portlets.interfaces import IPortletContext

from Testing.ZopeTestCase import user_name


class TestBasicContext(PortletsTestCase):

    def testParent(self):
        ctx = IPortletContext(self.folder)
        self.assertTrue(ctx.getParent() is self.folder.aq_parent)

    def testGlobalsNoGroups(self):
        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 3)
        self.assertEqual(g[0], ('content_type', 'Folder'))
        self.assertEqual(g[1], ('user', user_name))

    def testGlobalsWithSingleGroup(self):

        group = self.portal.portal_groups.getGroupById('Reviewers')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        group.addMember(user_name)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 4)
        self.assertEqual(g[0], ('content_type', 'Folder'))
        self.assertEqual(g[1], ('user', user_name))
        self.assertEqual(g[3], ('group', 'Reviewers'))

    def testGlobalsWithMultipleGroup(self):

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        group = self.portal.portal_groups.getGroupById('Reviewers')
        group.addMember(user_name)
        group = self.portal.portal_groups.getGroupById('Administrators')
        group.addMember(user_name)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 5)
        self.assertEqual(g[0], ('content_type', 'Folder'))
        self.assertEqual(g[1], ('user', user_name))
        self.assertEqual(g[2], ('group', 'Administrators'))
        self.assertEqual(g[4], ('group', 'Reviewers'))

    def testAnonymous(self):
        logout()
        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 2)
        self.assertEqual(g[0], ('content_type', 'Folder'))
        self.assertEqual(g[1], ('user', 'Anonymous User'))


class TestPortalRootContext(PortletsTestCase):

    def testParent(self):
        ctx = IPortletContext(self.portal)
        self.assertTrue(ctx.getParent() is None)

    def testGlobalsNoGroups(self):
        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 3)
        self.assertEqual(g[0], ('content_type', 'Plone Site'))
        self.assertEqual(g[1], ('user', user_name))

    def testGlobalsWithSingleGroup(self):

        group = self.portal.portal_groups.getGroupById('Reviewers')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        group.addMember(user_name)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 4)
        self.assertEqual(g[0], ('content_type', 'Plone Site'))
        self.assertEqual(g[1], ('user', user_name))
        self.assertEqual(g[3], ('group', 'Reviewers'))

    def testGlobalsWithMultipleGroup(self):

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        group = self.portal.portal_groups.getGroupById('Reviewers')
        group.addMember(user_name)
        group = self.portal.portal_groups.getGroupById('Administrators')
        group.addMember(user_name)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 5)
        self.assertEqual(g[0], ('content_type', 'Plone Site'))
        self.assertEqual(g[1], ('user', user_name))
        self.assertEqual(g[2], ('group', 'Administrators'))
        self.assertEqual(g[4], ('group', 'Reviewers'))

    def testAnonymous(self):
        logout()
        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEqual(len(g), 2)
        self.assertEqual(g[0], ('content_type', 'Plone Site'))
        self.assertEqual(g[1], ('user', 'Anonymous User'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasicContext))
    suite.addTest(makeSuite(TestPortalRootContext))
    return suite
