from five.intid.intid import IntIds
from five.intid.site import addUtility
from plone.app.portlets.portlets import navigation
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import INavigationRoot
from plone.base.interfaces import INavigationSchema
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.tests import dummy
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import directlyProvides
from zope.intid.interfaces import IIntIds

import unittest


class TestPortlet(PortletsTestCase):
    def afterSetUp(self):
        addUtility(self.portal, IIntIds, IntIds, ofs_name="intids", findroot=False)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name="portlets.Navigation")
        self.assertEqual(portlet.addview, "portlets.Navigation")

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name="portlets.Navigation")
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ["plone.app.portlets.interfaces.IColumn"], registered_interfaces
        )

    def testInterfaces(self):
        portlet = navigation.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name="portlets.Navigation")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], navigation.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping["foo"] = navigation.Assignment()
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        self.assertTrue(isinstance(editview, navigation.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.leftcolumn", context=self.portal
        )
        assignment = navigation.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, navigation.Renderer))


class TestRenderer(PortletsTestCase):
    def afterSetUp(self):
        addUtility(self.portal, IIntIds, IntIds, ofs_name="intids", findroot=False)

        self.populateSite()

    def renderer(
        self, context=None, request=None, view=None, manager=None, assignment=None
    ):
        context = context or self.portal
        request = request or self.request
        view = view or self.portal.restrictedTraverse("@@plone")
        manager = manager or getUtility(
            IPortletManager, name="plone.leftcolumn", context=self.portal
        )
        assignment = assignment or navigation.Assignment(topLevel=0)

        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )

    def populateSite(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        if "Members" in self.portal:
            self.portal._delObject("Members")
            self.folder = None
        if "news" in self.portal:
            self.portal._delObject("news")
        if "events" in self.portal:
            self.portal._delObject("events")
        if "front-page" in self.portal:
            self.portal._delObject("front-page")
        if "folder" in self.portal:
            self.portal._delObject("folder")
        if "users" in self.portal:
            self.portal._delObject("users")
        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.invokeFactory("Document", "doc3")
        self.portal.invokeFactory("Folder", "folder1")
        self.portal.invokeFactory("Link", "link1")
        self.portal.link1.remoteUrl = "http://plone.org"
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")
        folder1.invokeFactory("Document", "doc12")
        folder1.invokeFactory("Document", "doc13")
        self.portal.invokeFactory("Folder", "folder2")
        folder2 = getattr(self.portal, "folder2")
        folder2.invokeFactory("Document", "doc21")
        folder2.invokeFactory("Document", "doc22")
        folder2.invokeFactory("Document", "doc23")
        folder2.invokeFactory("File", "file21")
        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def testCreateNavTree(self):
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue("children" in tree)

    def testCreateNavTreeCurrentItem(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][-1]["currentItem"], True)

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items with the exclude_from_nav property set get
        # no_display set to True
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()
        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self.assertTrue(tree)
        for c in tree["children"]:
            if c["item"].getPath() == "/plone/folder2":
                self.fail()

    def testShowAllParentsOverridesNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property are not included
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()
        view = self.renderer(self.portal.folder2.doc21)
        tree = view.getNavTree()
        self.assertTrue(tree)
        found = False
        for c in tree["children"]:
            if c["item"].getPath() == "/plone/folder2":
                found = True
                break
        self.assertTrue(found)

    def testNavTreeExcludesDefaultPage(self):
        # Make sure that items which are the default page are excluded
        self.portal.folder2.setDefaultPage("doc21")
        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self.assertTrue(tree)
        # Ensure that our 'doc21' default page is not in the tree.
        self.assertEqual(
            [
                c
                for c in tree["children"][-1]["children"]
                if c["item"].getPath()[-5:] == "doc21"
            ],
            [],
        )

    def testNavTreeMarksParentMetaTypesNotToQuery(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get no_display set to True
        view = self.renderer(self.portal.folder2.file21)
        tree = view.getNavTree()
        self.assertEqual(tree["children"][-1]["show_children"], True)
        registry = self.portal.portal_registry
        registry["plone.parent_types_not_to_query"] = ["Folder"]
        view = self.renderer(self.portal.folder2.file21)
        tree = view.getNavTree()
        self.assertEqual(tree["children"][-1]["show_children"], False)

    def testCreateNavTreeWithLink(self):
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        for child in tree["children"]:
            if child["portal_type"] != "Link":
                self.assertFalse(child["getRemoteUrl"])
            if child["Title"] == "link1":
                self.assertEqual(child["getRemoteUrl"], "http://plone.org")
                # as Creator, link1 should not use the remote Url
                self.assertFalse(child["useRemoteUrl"])

        self.portal.link1.setCreators(["some_other_user"])
        self.portal.link1.reindexObject()
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        for child in tree["children"]:
            if child["portal_type"] != "Link":
                self.assertFalse(child["getRemoteUrl"])
            if child["Title"] == "link1":
                self.assertEqual(child["getRemoteUrl"], "http://plone.org")
                # as non-Creator user, link1 should use the remote Url
                self.assertTrue(child["useRemoteUrl"])

    def testNonStructuralFolderHidesChildren(self):
        # Make sure NonStructuralFolders act as if parent_types_not_to_query
        # is set.
        f = dummy.NonStructuralFolder("ns_folder")
        self.portal.folder1._setObject("ns_folder", f)
        self.portal.portal_catalog.reindexObject(self.portal.folder1.ns_folder)
        self.portal.portal_catalog.reindexObject(self.portal.folder1)
        view = self.renderer(self.portal.folder1.ns_folder)
        tree = view.getNavTree()
        self.assertEqual(
            tree["children"][3]["children"][3]["item"].getPath(),
            "/plone/folder1/ns_folder",
        )
        self.assertEqual(len(tree["children"][3]["children"][3]["children"]), 0)

    def testTopLevel(self):
        view = self.renderer(
            self.portal.folder2.file21, assignment=navigation.Assignment(topLevel=1)
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["children"][-1]["item"].getPath(), "/plone/folder2/file21"
        )

    def testTopLevelWithContextAboveLevel(self):
        view = self.renderer(self.portal, assignment=navigation.Assignment(topLevel=1))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 0)

    def testTopLevelTooDeep(self):
        view = self.renderer(self.portal, assignment=navigation.Assignment(topLevel=5))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 0)

    def testIncludeTopWithoutNavigationRoot(self):
        self.portal.folder2.invokeFactory("Folder", "folder21")
        self.portal.folder2.folder21.invokeFactory("Document", "doc211")
        view = self.renderer(
            self.portal.folder2.folder21,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=None, includeTop=True
            ),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue(view.root_is_portal())
        self.assertEqual(len(tree["children"]), 6)
        self.assertEqual(view.getNavRootPath(), "/plone")

    def testTopLevelWithNavigationRoot(self):
        self.portal.folder2.invokeFactory("Folder", "folder21")
        self.portal.folder2.folder21.invokeFactory("Document", "doc211")
        view = self.renderer(
            self.portal.folder2.folder21,
            assignment=navigation.Assignment(
                topLevel=1, root_uid=self.portal.folder2.UID()
            ),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(
            tree["children"][0]["item"].getPath(), "/plone/folder2/folder21/doc211"
        )

    def testMultipleTopLevelWithNavigationRoot(self):
        # See bug 9405
        # http://dev.plone.org/plone/ticket/9405
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "abc")
        self.portal.invokeFactory("Folder", "abcde")
        self.portal.abc.invokeFactory("Folder", "down_abc")
        self.portal.abcde.invokeFactory("Folder", "down_abcde")
        view1 = self.renderer(
            self.portal.abc,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=self.portal.abc.UID()
            ),
        )
        view2 = self.renderer(
            self.portal.abc,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=self.portal.abcde.UID()
            ),
        )
        tree1 = view1.getNavTree()
        tree2 = view2.getNavTree()
        self.assertEqual(len(tree1["children"]), 1)
        self.assertEqual(len(tree2["children"]), 1)
        view1 = self.renderer(
            self.portal.abcde,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=self.portal.abc.UID()
            ),
        )
        view2 = self.renderer(
            self.portal.abcde,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=self.portal.abcde.UID()
            ),
        )
        tree1 = view1.getNavTree()
        tree2 = view2.getNavTree()
        self.assertEqual(len(tree2["children"]), 1)
        self.assertEqual(len(tree1["children"]), 1)

    def testShowAllParentsOverridesBottomLevel(self):
        view = self.renderer(
            self.portal.folder2.file21,
            assignment=navigation.Assignment(bottomLevel=1, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        # Note: showAllParents makes sure we actually return items on the,
        # path to the context, but the portlet will not display anything
        # below bottomLevel.
        self.assertEqual(tree["children"][-1]["item"].getPath(), "/plone/folder2")
        self.assertEqual(len(tree["children"][-1]["children"]), 1)
        self.assertEqual(
            tree["children"][-1]["children"][0]["item"].getPath(),
            "/plone/folder2/file21",
        )

    def testBottomLevelStopsAtFolder(self):
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(bottomLevel=1, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][-1]["item"].getPath(), "/plone/folder2")
        self.assertEqual(len(tree["children"][-1]["children"]), 0)

    def testBottomLevelZeroNoLimit(self):
        """Test that bottomLevel=0 means no limit for bottomLevel."""

        # first we set a high integer as bottomLevel to simulate "no limit"
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(bottomLevel=99, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["children"][-1]["children"][0]["item"].getPath(),
            "/plone/folder2/doc21",
        )

        # now set bottomLevel to 0 -> outcome should be the same
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(bottomLevel=0, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["children"][-1]["children"][0]["item"].getPath(),
            "/plone/folder2/doc21",
        )

    def testBottomLevelZeroNoLimitRendering(self):
        """Test that bottomLevel=0 means no limit for bottomLevel."""

        # first we set a high integer as bottomLevel to simulate "no limit"
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(bottomLevel=99, topLevel=0),
        )
        a = view.render()

        # now set bottomLevel to 0 -> outcome should be the same
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(bottomLevel=0, topLevel=0),
        )
        b = view.render()

        self.assertEqual(a, b)

    def testNavRootWithUnicodeNavigationRoot(self):
        self.portal.folder2.invokeFactory("Folder", "folder21")
        self.portal.folder2.folder21.invokeFactory("Document", "doc211")
        view = self.renderer(
            self.portal.folder2.folder21,
            assignment=navigation.Assignment(
                topLevel=1, root_uid=self.portal.folder2.UID()
            ),
        )
        self.assertEqual(view.getNavRootPath(), "/plone/folder2/folder21")
        self.assertEqual(
            view.getNavRoot().absolute_url(),
            self.portal.folder2.folder21.absolute_url(),
        )

    def testNoRootSet(self):
        view = self.renderer(
            self.portal.folder2.file21,
            assignment=navigation.Assignment(root_uid="", topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][-1]["item"].getPath(), "/plone/folder2")

    def testRootIsNotPortal(self):
        view = self.renderer(
            self.portal.folder2.file21,
            assignment=navigation.Assignment(
                root_uid=self.portal.folder2.UID(), topLevel=0
            ),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder2/doc21")

    def testRootDoesNotExist(self):
        view = self.renderer(
            self.portal.folder2.file21,
            assignment=navigation.Assignment(root_uid="DOESNT_EXIST", topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 6)

    def testAboveRoot(self):
        registry = getUtility(IRegistry)
        registry["plone.root"] = "/folder2"
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder2/doc21")

    def testOutsideRoot(self):
        view = self.renderer(
            self.portal.folder1,
            assignment=navigation.Assignment(root_uid=self.portal.folder2.UID()),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder2/doc21")

    def testRootIsCurrent(self):
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(currentFolderOnly=True),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder2/doc21")

    def testRootIsCurrentWithFolderishDefaultPage(self):
        self.portal.folder2.invokeFactory("Folder", "folder21")
        self.portal.folder2.setDefaultPage("folder21")

        view = self.renderer(
            self.portal.folder2.folder21,
            assignment=navigation.Assignment(currentFolderOnly=True),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder2/doc21")

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct["PythonScripts"]
        factory.manage_addPythonScript("getCustomNavQuery")
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit("", 'return {"review_state": "published"}')
        self.assertEqual(self.portal.getCustomNavQuery(), {"review_state": "published"})
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue("children" in tree)
        # Should only contain current object
        self.assertEqual(len(tree["children"]), 1)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        # Should only contain current object and published folder
        self.assertEqual(len(tree["children"]), 2)

    def testStateFiltering(self):
        # Test Navtree workflow state filtering
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(INavigationSchema, prefix="plone")
        workflow = self.portal.portal_workflow
        navigation_settings.workflow_states_to_show = ("published",)
        navigation_settings.filter_on_workflow = True
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue("children" in tree)
        # Should only contain current object
        self.assertEqual(len(tree["children"]), 1)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        # Should only contain current object and published folder
        self.assertEqual(len(tree["children"]), 2)

    def testPrunedRootNode(self):
        registry = self.portal.portal_registry
        registry["plone.parent_types_not_to_query"] = ["Folder"]

        assignment = navigation.Assignment(topLevel=0)
        assignment.topLevel = 1
        view = self.renderer(self.portal.folder1, assignment=assignment)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 0)

    def testPrunedRootNodeShowsAllParents(self):
        registry = self.portal.portal_registry
        registry["plone.parent_types_not_to_query"] = ["Folder"]

        assignment = navigation.Assignment(topLevel=0)
        assignment.topLevel = 1
        view = self.renderer(self.portal.folder1.doc11, assignment=assignment)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(tree["children"][0]["item"].getPath(), "/plone/folder1/doc11")

    def testIsCurrentParentWithOverlapingNames(self):
        setRoles(
            self.portal,
            TEST_USER_ID,
            [
                "Manager",
            ],
        )
        self.portal.invokeFactory("Folder", "folder2x")
        self.portal.folder2x.invokeFactory("Document", "doc2x1")
        setRoles(
            self.portal,
            TEST_USER_ID,
            [
                "Member",
            ],
        )
        view = self.renderer(self.portal.folder2x.doc2x1)
        tree = view.getNavTree()
        self.assertTrue(tree)

        folder2x_node = [n for n in tree["children"] if n["path"] == "/plone/folder2x"][
            0
        ]
        self.assertTrue(folder2x_node["currentParent"])

        folder2_node = [n for n in tree["children"] if n["path"] == "/plone/folder2"][0]
        self.assertFalse(folder2_node["currentParent"])

    def testPortletNotDisplayedOnINavigationRoot(self):
        """test that navigation portlet does not show on INavigationRoot
        folder
        """
        self.assertFalse(INavigationRoot.providedBy(self.portal.folder1))

        # make folder1 as navigation root
        directlyProvides(self.portal.folder1, INavigationRoot)
        self.assertTrue(INavigationRoot.providedBy(self.portal.folder1))

        # add nested subfolder in folder1
        self.portal.folder1.invokeFactory("Folder", "folder1_1")

        # make a navigation portlet
        assignment = navigation.Assignment(bottomLevel=0, topLevel=1, root_uid=None)
        portlet = self.renderer(self.portal.folder1, assignment=assignment)

        # check there is no portlet
        self.assertFalse(portlet.available)

    def testINavigationRootWithRelativeRootSet(self):
        """test that navigation portlet uses relative root set by user
        even in INavigationRoot case.
        """
        self.assertFalse(INavigationRoot.providedBy(self.portal.folder1))

        # make folder1 as navigation root
        directlyProvides(self.portal.folder1, INavigationRoot)
        self.assertTrue(INavigationRoot.providedBy(self.portal.folder1))

        # add two nested subfolders in folder1
        self.portal.folder1.invokeFactory("Folder", "folder1_1")
        self.portal.folder1.folder1_1.invokeFactory("Folder", "folder1_1_1")

        # make a navigation portlet with navigation root set
        assignment = navigation.Assignment(
            bottomLevel=0, topLevel=0, root_uid=self.portal.folder1.folder1_1.UID()
        )
        portlet = self.renderer(self.portal.folder1.folder1_1, assignment=assignment)

        # check there is a portlet
        self.assertTrue(portlet.available)

        # check that portlet root is actually the one specified
        root = portlet.getNavRoot()
        self.assertEqual(root.getId(), "folder1_1")

        # check that portlet tree actually includes children
        tree = portlet.getNavTree()
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(
            tree["children"][0]["item"].getPath(),
            "/plone/folder1/folder1_1/folder1_1_1",
        )

    def testPortletsTitle(self):
        """If portlet's name is not explicitly specified we show
        default fallback 'Navigation', translate it and hide it
        with CSS."""
        view = self.renderer(self.portal)
        view.getNavTree()
        self.assertEqual(view.title(), "Navigation")
        self.assertFalse(view.hasName())
        view.data.name = "New navigation title"
        self.assertEqual(view.title(), "New navigation title")
        self.assertTrue(view.hasName())

    def testHeadingLinkRootless(self):
        """
        See that heading link points to a global sitemap if no root item is set.
        """

        directlyProvides(self.portal.folder2, INavigationRoot)
        view = self.renderer(
            self.portal.folder2, assignment=navigation.Assignment(topLevel=0)
        )
        link = view.heading_link_target()
        # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://nohost/plone/folder2/sitemap")

        # Even if the assignment contains no topLevel options and no self.root
        # one should get link to the navigation root sitemap
        view = self.renderer(
            self.portal.folder2.doc21, assignment=navigation.Assignment()
        )
        link = view.heading_link_target()
        # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://nohost/plone/folder2/sitemap")

        view = self.renderer(
            self.portal.folder1, assignment=navigation.Assignment(topLevel=0)
        )
        link = view.heading_link_target()
        # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://nohost/plone/sitemap")

    def testHeadingLinkRooted(self):
        """
        See that heading link points to a content item if root selected, otherwise sitemap.
        """
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(
                topLevel=0, root_uid=self.portal.folder2.UID()
            ),
        )
        link = view.heading_link_target()
        self.assertEqual(link, "http://nohost/plone/folder2")

    def testHeadingLinkRootedItemGone(self):
        """
        See that heading link points to a content item which do not exist
        """
        view = self.renderer(
            self.portal.folder2,
            assignment=navigation.Assignment(topLevel=0, root_uid="DOESNT_EXIST"),
        )
        link = view.heading_link_target()
        # Points to the site root if the item is gone
        self.assertEqual(link, "http://nohost/plone/sitemap")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestPortlet))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestRenderer))
    return suite
