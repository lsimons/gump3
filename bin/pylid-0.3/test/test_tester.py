import unittest
import pylid


class uTester(unittest.TestCase):
    def setUp(self):
        self.tt = pylid.Tester(".", "..", "..")

    def test_addPath(self):
        self.tt.addPath("testTester/addPath/one.py", 0)
        self.failUnlessEqual(self.tt.suite.countTestCases(), 1)

    def test_addPathDir(self):
        self.tt.addPath("testTester/addPath/dir", 0)
        self.failUnlessEqual(self.tt.suite.countTestCases(), 2)


def makeSuite():
    suite = unittest.makeSuite(uTester)
    return suite
