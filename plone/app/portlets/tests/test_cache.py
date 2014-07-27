# -*- coding: utf-8 -*-
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.cache import render_cachekey
from plone.app.testing import logout


class MockBrain(object):

    def __init__(self, path=u"some/path", modified=u"2002-01-01"):
        self.path = path
        self.modified = modified

    def getPath(self):
        return self.path


class MockLocation(object):

    def __init__(self, name):
        self.__name__ = name


class MockRenderer(object):
    manager = MockLocation('some_manager')
    data = MockLocation('some_assignment')
    data_brains = [MockBrain(), MockBrain()]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _data(self):
        return self.data_brains


class TestCacheKey(PortletsTestCase):

    def testRenderCachekey(self):
        context = self.folder
        renderer = MockRenderer(context, context.REQUEST)

        key1 = render_cachekey(None, renderer)
        renderer.manager.__name__ += '__changed__'
        key2 = render_cachekey(None, renderer)

        self.assertTrue(key1 != key2)

    def testAnonymousFlag(self):
        context = self.folder
        renderer = MockRenderer(context, context.REQUEST)

        key1 = render_cachekey(None, renderer)
        logout()
        key2 = render_cachekey(None, renderer)

        self.assertNotEqual(key1, key2)

    def testNonASCIIPath(self):
        # http://dev.plone.org/plone/ticket/7086
        context = self.folder
        renderer = MockRenderer(context, context.REQUEST)
        renderer.data_brains = [
            MockBrain("Pr\xc5\xafvodce"), MockBrain("p\xc5\x99i")]
        render_cachekey(None, renderer)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCacheKey))
    return suite
