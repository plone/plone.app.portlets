from plone.app.portlets.tests.base import PortletsTestCase
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletType
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.PropertiedUser import PropertiedUser
from unittest import makeSuite
from unittest import TestSuite
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify


class TestDashboard(PortletsTestCase):
    def test_default_dashboard_created_for_new_user(self):

        col = getUtility(IPortletManager, name="plone.dashboard1")
        user_portlets = col[USER_CATEGORY]
        self.assertFalse("fakeuser" in user_portlets)

        # This would normally happen when a user is created
        notify(PrincipalCreated(PropertiedUser("fakeuser")))

        # We would expect some portlets to have been created after the
        # event handler has finished processing

        self.assertTrue("fakeuser" in user_portlets)
        self.assertTrue(len(user_portlets["fakeuser"]) > 0)

    def test_non_ascii_usernames_created(self):
        user1, pass1 = "user1\xa9", "pass1"
        uf = self.portal.acl_users

        # Bug #6100 - Would throw a unicode decode error in event handler
        # in dashboard.py
        uf.userFolderAddUser(user1, pass1, ["Manager"], [])

        col = getUtility(IPortletManager, name="plone.dashboard1")
        retriever = getMultiAdapter((self.portal, col), IPortletRetriever)

        # Bug #7860 - Would throw a unicode decode error when fetching
        # portlets
        retriever.getPortlets()


def test_suite():

    suite = TestSuite()
    suite.addTest(makeSuite(TestDashboard))
    return suite
