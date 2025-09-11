from plone.app.portlets.tests.base import PortletsTestCase

import unittest


class TestManageAssignments(PortletsTestCase):
    def testMoveUp(self):
        self.fail("Test missing")

    def testMoveDown(self):
        self.fail("Test missing")

    def testDelete(self):
        self.fail("Test missing")


def test_suite():
    suite = unittest.TestSuite()
    # TODO: Write tests that *pass*
    # suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestManageAssignments))
    return suite
