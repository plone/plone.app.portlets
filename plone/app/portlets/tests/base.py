"""Base class for integration tests."""
from plone.app.portlets.testing import PLONE_APP_PORTLETS_INTEGRATION_TESTING

import unittest


class PortletsTestCase(unittest.TestCase):
    """Base class for integration tests for plone.app.portlets. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

    layer = PLONE_APP_PORTLETS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.folder = self.portal["folder"]
        self.request = self.layer["request"]

        self.afterSetUp()

    def afterSetUp(self):
        pass
