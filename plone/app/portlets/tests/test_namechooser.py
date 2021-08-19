from plone.app.portlets.testing import OPTIONFLAGS
from plone.app.portlets.testing import PLONE_APP_PORTLETS_INTEGRATION_TESTING
from plone.testing import layered

import doctest
import unittest


def test_suite():

    import plone.app.portlets.storage

    return unittest.TestSuite(
        [
            layered(
                doctest.DocTestSuite(
                    module=plone.app.portlets.storage,
                    optionflags=OPTIONFLAGS,
                ),
                layer=PLONE_APP_PORTLETS_INTEGRATION_TESTING,
            )
        ]
    )
