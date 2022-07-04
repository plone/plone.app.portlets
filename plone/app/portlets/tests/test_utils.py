from plone.app.portlets.browser.utils import PortletUtilities
from plone.app.portlets.portlets import classic
from plone.app.portlets.portlets import news
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.utils import assignment_from_key
from plone.app.testing import TEST_USER_ID
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.utils import hashPortletInfo
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestAssignmentFromKey(PortletsTestCase):
    def afterSetUp(self):
        self.manager = getUtility(IPortletManager, name="plone.leftcolumn")
        self.cat = self.manager[USER_CATEGORY]
        self.cat[TEST_USER_ID] = PortletAssignmentMapping(
            manager="plone.leftcolumn", category=USER_CATEGORY, name=TEST_USER_ID
        )

    def testGetPortletFromContext(self):
        mapping = getMultiAdapter(
            (self.portal, self.manager), IPortletAssignmentMapping
        )
        c = classic.Assignment()
        mapping["foo"] = c
        path = "/".join(self.portal.getPhysicalPath())
        a = assignment_from_key(
            self.portal, "plone.leftcolumn", CONTEXT_CATEGORY, path, "foo"
        )
        self.assertEqual(c, a)

    def testGetPortletFromContextUnicodePath(self):
        """Do not fail, if path is a unicode object.
        plone.portlets.utils.unhashPortletInfo returns a unicode path key.
        """
        mapping = getMultiAdapter(
            (self.portal, self.manager), IPortletAssignmentMapping
        )
        c = classic.Assignment()
        mapping["foo"] = c
        path = "/".join(self.portal.getPhysicalPath())
        a = assignment_from_key(
            self.portal, "plone.leftcolumn", CONTEXT_CATEGORY, path, "foo"
        )
        self.assertEqual(c, a)

    def testGetPortletFromUserCategory(self):
        c = classic.Assignment()
        self.cat[TEST_USER_ID]["foo"] = c
        a = assignment_from_key(
            self.portal, "plone.leftcolumn", USER_CATEGORY, TEST_USER_ID, "foo"
        )
        self.assertEqual(c, a)


class TestRendering(PortletsTestCase):
    def afterSetUp(self):
        self.portal.invokeFactory("News Item", "testnews", title="Test News")

    def testTraversalRendererWithHash(self):
        context = self.folder
        request = self.folder.REQUEST
        manager = getUtility(
            IPortletManager, name="plone.leftcolumn", context=self.folder
        )
        assignment = news.Assignment(state=("private",))
        mapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
        mapping["newsportlet"] = assignment
        portlet_hash = hashPortletInfo(
            dict(
                manager=manager.__name__,
                category=CONTEXT_CATEGORY,
                key="/".join(context.getPhysicalPath()),
                name="newsportlet",
            )
        )
        render_portlet_view = PortletUtilities(context, request)
        rendered_portlet = render_portlet_view.render_portlet(
            safe_unicode(portlet_hash)
        )
        self.assertIn("portletNews", rendered_portlet)
        self.assertIn("Test News", rendered_portlet)


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestAssignmentFromKey))
    suite.addTest(makeSuite(TestRendering))
    return suite
