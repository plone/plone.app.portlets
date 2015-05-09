"""Base class for integration tests, based on ZopeTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

import unittest2 as unittest

from Testing.ZopeTestCase import Functional
from plone.app.portlets.testing import PLONE_APP_PORTLETS_INTEGRATION_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser


class PortletsTestCase(unittest.TestCase):
    """Base class for integration tests for plone.app.portlets. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

    layer = PLONE_APP_PORTLETS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        self.request = self.layer['request']

        self.afterSetUp()

    def afterSetUp(self):
        pass


class PortletsFunctionalTestCase(unittest.TestCase, Functional):
    """Base class for functional integration tests for plone.app.portlets.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    layer = PLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = True
        self.app.acl_users.userFolderAddUser('app', 'secret', ['Manager'], [])
        from plone.testing import z2
        z2.login(self.app['acl_users'], 'app')

        import transaction
        transaction.commit()
        self.site_administrator_browser = Browser(self.app)
        self.site_administrator_browser.handleErrors = False
        self.site_administrator_browser.addHeader(
            'Authorization',
            'Basic %s:%s' % ('app', 'secret')
        )
