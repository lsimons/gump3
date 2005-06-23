
import unittest, os.path
from pylid import isPathContained, summariseList

class uUtils(unittest.TestCase):
    def test_isPathContained(self):
        self.failUnless(isPathContained(os.path.abspath("."), "./foo.py"))
        self.failUnless(isPathContained(os.path.abspath(".."), "."))
        self.failIf(isPathContained(os.path.abspath("."), "../foo.py"))
        self.failUnless(isPathContained(os.path.abspath("."), "."))
        self.failUnless(isPathContained(os.path.abspath("../foo.py"), "../foo.py"))

    def test_summariseList(self):
        lst = [1, 2, 3, 4, 5]
        expected = [(1, 5)]
        self.failUnless(summariseList(lst) == expected)

        lst = []
        expected = []
        self.failUnless(summariseList(lst) == expected)
        
        lst = [1]
        expected = [1]
        self.failUnless(summariseList(lst) == expected)

        lst = [1, 2, 3, 8, 11, 12, 13, 15, 16, 17, 23]
        expected = [(1, 3), 8, (11, 13), (15, 17), 23]
        self.failUnless(summariseList(lst) == expected)


def makeSuite():
    suite = unittest.makeSuite(uUtils)
    return suite
