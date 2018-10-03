# -*- coding: utf-8 -*-
from plone.app.portlets.tests.base import PortletsFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite
from unittest import TestSuite

import doctest


def test_suite():
    suite = TestSuite()
    OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    suite.addTest(
        FunctionalDocFileSuite(
            'testMemberDashboard.rst',
            optionflags=OPTIONFLAGS,
            package="plone.app.portlets.tests",
            test_class=PortletsFunctionalTestCase,
        ),
    )
    return suite
