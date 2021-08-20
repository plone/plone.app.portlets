from plone.app.portlets.portlets import rss
from plone.app.portlets.testing import PLONE_APP_PORTLETS_FUNCTIONAL_TESTING
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility

import os
import transaction
import unittest


# Take a sample feed.  In this case an atom feed instead of RSS.
# Taken from https://maurits.vanrees.org/weblog/topics/plone/@@atom.xml
here = os.path.dirname(__file__)
sample_feed = os.path.join(here, "atom_feed_maurits.xml")


class TestPortlet(PortletsTestCase):
    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name="portlets.rss")
        self.assertEqual(portlet.addview, "portlets.rss")

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name="portlets.rss")
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            [
                "plone.app.portlets.interfaces.IColumn",
                "plone.app.portlets.interfaces.IDashboard",
            ],
            registered_interfaces,
        )

    def testInterfaces(self):
        portlet = rss.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name="portlets.rss")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], rss.Assignment))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )
        assignment = rss.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, rss.Renderer))

    def testRSSFeedFile(self):
        # We should not be able to read a file from the file system.
        # We pass a url and a timeout in minutes
        feed = rss.RSSFeed("file://" + sample_feed, 1)
        feed._retrieveFeed()
        self.assertTrue(feed._loaded)
        self.assertTrue(feed._failed)
        self.assertFalse(feed.ok)
        self.assertFalse(feed.siteurl)
        self.assertEqual(len(feed.items), 0)


class TestRenderer(PortletsTestCase):
    def renderer(
        self, context=None, request=None, view=None, manager=None, assignment=None
    ):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse("@@plone")
        manager = manager or getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )
        assignment = assignment or rss.Assignment()

        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )

    def test_rss_items(self):
        r = self.renderer(assignment=rss.Assignment())
        self.assertEqual(False, r.enabled)

    def testTitle(self):
        r = self.renderer(assignment=rss.Assignment())
        self.assertEqual(r.title, "")
        r.data.portlet_title = "Overridden title"
        self.assertEqual(r.title, "Overridden title")


class TestFunctional(unittest.TestCase):
    layer = PLONE_APP_PORTLETS_FUNCTIONAL_TESTING

    def test_rss_feed_http(self):
        # First prepare a file in the current site,
        # so that we can try to load this via http.
        with open(sample_feed, "rb") as myfile:
            data = myfile.read()
        file_field = NamedBlobFile(data, filename="feed.xml")
        portal = self.layer["portal"]
        feed_id = portal.invokeFactory("File", "feed")
        feed = portal[feed_id]
        feed.file = file_field
        transaction.commit()

        # Eat the feed.
        feed = rss.RSSFeed(feed.absolute_url(), 1)
        feed._retrieveFeed()
        self.assertTrue(feed._loaded)
        self.assertFalse(feed._failed)
        self.assertTrue(feed.ok)
        self.assertEqual(feed.siteurl, "https://maurits.vanrees.org/weblog")
        self.assertEqual(len(feed.items), 15)


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
