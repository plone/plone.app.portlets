from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig

import doctest


class PloneAppPortlets(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, "plone.app.portlets")

        # Include testing profile
        import plone.app.portlets

        xmlconfig.file(
            "configure.zcml", plone.app.portlets.tests, context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.contenttypes:default")

        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)

        # Prepare test content
        pw = getToolByName(portal, "portal_workflow")
        pw.setDefaultChain("simple_publication_workflow")
        portal.invokeFactory("Folder", id="folder", title="Test Folder")
        portal.invokeFactory("Folder", id="news", title="News")
        portal.invokeFactory("Folder", id="users", title="Users")
        portal.invokeFactory("Folder", id="events", title="Events")
        pw.doActionFor(portal.news, "publish")


PLONE_APP_PORTLETS_FIXTURE = PloneAppPortlets()
PLONE_APP_PORTLETS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_PORTLETS_FIXTURE,),
    name="PloneAppPortlets:Integration",
)
PLONE_APP_PORTLETS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_PORTLETS_FIXTURE,),
    name="PloneAppPortlets:Functional",
)

OPTIONFLAGS = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)
