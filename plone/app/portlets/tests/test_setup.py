from plone.app.portlets.interfaces import IDashboard
from plone.app.portlets.interfaces import ILeftColumn
from plone.app.portlets.interfaces import IRightColumn
from plone.app.portlets.tests.base import PortletsTestCase
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import getUtility


class TestProductInstall(PortletsTestCase):
    def testPortletManagersRegistered(self):
        sm = getSiteManager(self.portal)
        registrations = [
            r.name for r in sm.registeredUtilities() if IPortletManager == r.provided
        ]
        self.assertEqual(
            [
                "plone.dashboard1",
                "plone.dashboard2",
                "plone.dashboard3",
                "plone.dashboard4",
                "plone.footerportlets",
                "plone.leftcolumn",
                "plone.rightcolumn",
            ],
            sorted(registrations),
        )

    def testInterfaces(self):
        left = getUtility(IPortletManager, "plone.leftcolumn")
        right = getUtility(IPortletManager, "plone.rightcolumn")
        dashboard = getUtility(IPortletManager, "plone.dashboard1")

        self.assertTrue(ILeftColumn.providedBy(left))
        self.assertTrue(IRightColumn.providedBy(right))
        self.assertTrue(IDashboard.providedBy(dashboard))

    def testAssignable(self):
        self.assertTrue(ILocalPortletAssignable.providedBy(self.folder))
        self.assertTrue(ILocalPortletAssignable.providedBy(self.portal))

    def testPortletTypesRegistered(self):
        portlets = [u[0] for u in getUtilitiesFor(IPortletType)]
        self.assertTrue("portlets.Classic" in portlets)
        self.assertTrue("portlets.Login" in portlets)


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
