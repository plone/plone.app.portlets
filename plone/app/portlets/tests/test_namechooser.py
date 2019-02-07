# -*- coding: utf-8 -*-
import unittest
import doctest

from plone.testing import layered
from plone.app.portlets.testing import PLONE_APP_PORTLETS_INTEGRATION_TESTING
from plone.app.portlets.testing import OPTIONFLAGS


def test_suite():

    import plone.app.portlets.storage

    return unittest.TestSuite([
        layered(
            doctest.DocTestSuite(
                module=plone.app.portlets.storage,
                optionflags=OPTIONFLAGS,
            ),
            layer=PLONE_APP_PORTLETS_INTEGRATION_TESTING,
        )
    ])
