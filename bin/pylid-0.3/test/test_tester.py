import unittest
import pylid
import sys

class uTester(unittest.TestCase):
    def setUp(self):
        self.tt = pylid.Tester(".", "..", "..")

    def test_addPath(self):
        self.tt.addPath("testTester/addPath/one.py", 0)
        self.failUnlessEqual(self.tt.suite.countTestCases(), 1)

    def test_addPathDir(self):
        self.tt.addPath("testTester/addPath/dir", 0)
        self.failUnlessEqual(self.tt.suite.countTestCases(), 2)
    
    def test_singleBaseDir(self):
        tt = pylid.Tester(".", "..", "..")
        self.assert_("." in sys.path)

    def test_multipleBaseDir(self):
        tt = pylid.Tester([".", "blah", "blah/blah"], "..", "..")
        self.assert_("." in sys.path)
        self.assert_("blah" in sys.path)
        self.assert_("blah/blah" in sys.path)

def makeSuite():
    suite = unittest.makeSuite(uTester)
    return suite
