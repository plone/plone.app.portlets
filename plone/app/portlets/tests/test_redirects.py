from plone.app.portlets.browser.adding import PortletAdding
from plone.app.portlets.browser.editmanager import ManagePortletAssignments
from plone.app.portlets.browser.formhelper import AddForm
from plone.app.portlets.browser.formhelper import EditForm
from plone.app.portlets.tests.base import PortletsTestCase


class TestRedirects(PortletsTestCase):
    _test_methods = [
        (PortletAdding, "nextURL"),
        (ManagePortletAssignments, "_nextUrl"),
        (AddForm, "nextURL"),
        (EditForm, "nextURL"),
    ]

    def test_regression(self):
        portal_url = self.portal.absolute_url()
        self.request.form.update({"referer": portal_url})
        for Klass, method in self._test_methods:
            view = Klass(self.portal, self.request)
            view.__parent__ = self.portal
            self.assertEqual(getattr(view, method)(), portal_url)

    def test_valid_next_url(self):
        self.request.form.update({"referer": "http://attacker.com"})
        for Klass, method in self._test_methods:
            view = Klass(self.portal, self.request)
            view.__parent__ = self.portal
            self.assertNotEqual("http://attacker.com", getattr(view, method)())


def test_suite():
    # Without this test_suite, there is a strange error when running the tests:
    #
    # Error in test runTest
    # (plone.app.portlets.tests.base.PortletsFunctionalTestCase)
    # Traceback (most recent call last):
    #   File "unittest2-0.5.1-py2.7.egg/unittest2/case.py", line 340, in run
    #     testMethod()
    #   TypeError: 'NoneType' object is not callable
    #
    # You get the error when running
    # bin/test -s plone.app.portlets
    # or
    # bin/test -s plone.app.portlets -t run
    # but not with
    # bin/test -s plone.app.portlets -m test_redirects
    # But the error *is* in this test_redirects.py file,
    # because it goes away when I delete this file.
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestRedirects))
    return suite
