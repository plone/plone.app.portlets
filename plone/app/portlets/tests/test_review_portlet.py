from plone.app.portlets.portlets import review
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestPortlet(PortletsTestCase):
    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name="portlets.Review")
        self.assertEqual(portlet.addview, "portlets.Review")

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name="portlets.Review")
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
        portlet = review.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name="portlets.Review")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], review.Assignment))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )
        assignment = review.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, review.Renderer))


class TestRenderer(PortletsTestCase):
    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.portal_membership.getMemberById("test_user_1_").setMemberProperties(
            {"fullname": "Test user"}
        )

        # add Folder and assign Reviewer role to our Test user there
        self.portal.invokeFactory("Folder", "folder1")
        self.folder1 = self.portal.folder1
        self.folder1.manage_setLocalRoles("test_user_1_", ["Reviewer"])
        self.folder1.reindexObjectSecurity()

    def renderer(
        self, context=None, request=None, view=None, manager=None, assignment=None
    ):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse("@@plone")
        manager = manager or getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )
        assignment = assignment or review.Assignment()

        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )

    def test_review_items(self):
        r = self.renderer(assignment=review.Assignment())
        self.assertEqual(0, len(r.review_items()))
        wf = getToolByName(self.portal, "portal_workflow")
        wf.doActionFor(self.portal.doc1, "submit")
        r = self.renderer(assignment=review.Assignment())
        self.assertEqual(1, len(r.review_items()))
        self.assertEqual(r.review_items()[0]["creator"], "Test user")

    def test_full_news_link(self):
        r = self.renderer(assignment=review.Assignment())
        self.assertTrue(r.full_review_link().endswith("/full_review_list"))

    def test_full_news_link_local_reviewer(self):
        # login as our test user
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Member"])

        # there should be no full news link on site root for our local reviewer
        r = self.renderer(assignment=review.Assignment())
        self.assertFalse(r.full_review_link())

        # get renderer in context of our reviewer's folder
        r = self.renderer(context=self.folder1, assignment=review.Assignment())
        self.assertEqual(
            r.full_review_link(), "%s/full_review_list" % self.folder1.absolute_url()
        )

    def test_title(self):
        r = self.renderer(assignment=review.Assignment())
        self.assertEqual(str(r.title), "box_review_list")


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
