from plone.app.portlets.portlets import actions
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestPortlet(PortletsTestCase):
    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name="portlets.Actions")
        self.assertEquals(portlet.addview, "portlets.Actions")
        return

    def test_interfaces(self):
        portlet = actions.Assignment(
            ptitle="actions", category="document", show_icons=True
        )
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))
        return

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name="portlets.Actions")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)

        data = {"ptitle": "Actions", "category": "document", "show_icons": True}
        addview.createAndAdd(data=data)

        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], actions.Assignment))
        return

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping["foo"] = actions.Assignment(
            ptitle="actions", category="document", show_icons=True
        )
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        self.assertTrue(isinstance(editview, actions.EditForm))
        return

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )

        assignment = actions.Assignment(
            ptitle="actions", category="document", show_icons=True
        )

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, actions.Renderer))
        return


class TestRenderer(PortletsTestCase):
    def afterSetUp(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def renderer(
        self, context=None, request=None, view=None, manager=None, assignment=None
    ):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse("@@plone")
        manager = manager or getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )

        assignment = assignment or actions.Assignment(
            ptitle="actions", category="site_actions", show_icons=True
        )
        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )

    def test_render(self):
        migtool = getToolByName(self.portal, "portal_migration")

        r = self.renderer(
            context=self.portal,
            assignment=actions.Assignment(
                ptitle="actions", category="site_actions", show_icons=True
            ),
        )
        r.update()
        output = r.actionLinks()

        if int(migtool.getInstanceVersion()[0]) >= 4:
            self.assertEqual(len(output), 3)
        else:
            self.assertEqual(len(output), 4)

        first = output[0]
        self.assertEqual(first["url"], "http://nohost/plone/sitemap")
        self.assertEqual(first["title"], "Site Map")

    def test_render_woicon(self):
        """Without icons"""
        r = self.renderer(
            context=self.portal,
            assignment=actions.Assignment(
                ptitle="actions", category="site_actions", show_icons=False
            ),
        )
        r.update()
        output = r.actionLinks()
        first = output[0]
        self.assertTrue(first["icon"] is None, "We should not have an icon")
        return

    def test_multiple_portlets(self):
        """This test ensures that we can add more than one action portlet on
        the same page with different action categories and show_icons option
        and those portlets will work as they are intended to work.

        This test was written due to bug caused by caching actionLinks portlet
        renderer's method
        """
        migtool = getToolByName(self.portal, "portal_migration")

        # let's create two different portlet renderers for the same context
        # thus for the same REQUEST, plone memoize uses REQUEST to cache data
        r1 = self.renderer(
            assignment=actions.Assignment(
                ptitle="tabs", category="portal_tabs", show_icons=True
            )
        )
        r1.update()
        links1 = r1.actionLinks()
        r2 = self.renderer(
            assignment=actions.Assignment(
                ptitle="site actions", category="site_actions", show_icons=False
            )
        )
        r2.update()
        links2 = r2.actionLinks()

        # check the portal_tabs links (portal_tabs is somehow special)
        self.assertEquals(len(links1), 5)
        self.assertEquals(links1[0]["title"], "Home")

        # now check the site_actions links
        # this was failing until the caching of actionLinks method was fixed
        if int(migtool.getInstanceVersion()[0]) >= 4:
            self.assertEquals(len(links2), 3)
        else:
            self.assertEquals(len(links2), 4)
        self.assertEquals(links2[0]["title"], "Site Map")
        self.assertEquals(links2[0]["url"], "http://nohost/plone/sitemap")
        self.assertEquals(links2[0]["icon"], None)
        return

    def test_portal_tabs(self):
        """Special stuff for the portal_tabs category which actions rely on
        content in Plone content root
        """
        r = self.renderer(
            context=self.portal,
            assignment=actions.Assignment(
                ptitle="actions", category="portal_tabs", show_icons=True
            ),
        )
        r.update()
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = {"Test Folder", "Home", "Users", "News", "Events"}
        got = {str(link["title"]) for link in output}
        self.assertEqual(got, expected)

    def test_object_buttons(self):
        """Special stuff for the object_buttons category"""
        r = self.renderer(
            context=self.portal["news"],
            assignment=actions.Assignment(
                ptitle="actions", category="object_buttons", show_icons=False
            ),
        )
        r.update()
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = {"Cut", "Copy", "Rename", "Delete"}
        got = {str(link["title"]) for link in output}
        self.assertTrue(expected.issubset(got))

    def test_category(self):
        r = self.renderer(
            context=self.portal["news"],
            assignment=actions.Assignment(
                ptitle="actions", category="object_buttons", show_icons=False
            ),
        )
        r.update()
        self.assertEqual(r.category, "object_buttons")

    def test_category_normalize(self):
        class DummyData:
            category = "Complex Category"

        r = actions.Renderer(None, None, None, None, DummyData())
        self.assertEqual(r.category, "complex-category")

    def test_object_buttons_with_icons(self):
        """Special stuff for the object_buttons category (bug in render_icons)"""
        r = self.renderer(
            context=self.portal["news"],
            assignment=actions.Assignment(
                ptitle="actions", category="object_buttons", show_icons=True
            ),
        )
        r.update()
        self.assertTrue(r.actionLinks)
        output = r.actionLinks()

        # Have our expected tabs ?
        expected = {"Cut", "Copy", "Rename", "Delete"}
        got = {str(link["title"]) for link in output}
        self.assertTrue(expected.issubset(got))
