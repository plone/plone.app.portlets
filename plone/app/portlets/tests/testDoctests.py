# -*- coding: utf-8 -*-
from plone.app.portlets.testing import OPTIONFLAGS
from plone.app.portlets.testing import PLONE_APP_PORTLETS_FUNCTIONAL_TESTING
from plone.testing import layered
from unittest import TestSuite

import doctest
import re
import six


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub(
                'LocationError', 'zope.location.interfaces.LocationError', got
            )
            got = re.sub("u'(.*?)'", "'\\1'", got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = TestSuite()
    suite.addTest(
        layered(
            doctest.DocFileSuite(
                'testMemberDashboard.rst',
                checker=Py23DocChecker(),
                package='plone.app.portlets.tests',
                optionflags=OPTIONFLAGS,
            ),
            layer=PLONE_APP_PORTLETS_FUNCTIONAL_TESTING
        )
    )
    return suite
