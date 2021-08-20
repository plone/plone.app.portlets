from doctest import DocFileSuite
from plone.app.portlets.testing import OPTIONFLAGS
from plone.app.portlets.testing import PLONE_APP_PORTLETS_FUNCTIONAL_TESTING
from plone.testing import layered
from unittest import TestSuite


def test_suite():
    suite = TestSuite()
    suite.addTest(
        layered(
            DocFileSuite(
                "testMemberDashboard.rst",
                package="plone.app.portlets.tests",
                optionflags=OPTIONFLAGS,
            ),
            layer=PLONE_APP_PORTLETS_FUNCTIONAL_TESTING,
        )
    )
    return suite
