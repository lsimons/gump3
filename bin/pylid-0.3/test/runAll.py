#!/usr/bin/env python

import unittest, os, sys, fnmatch, glob

def makeSuite():
    """
        Build a test suite of all available test files.
    """
    allTests = unittest.TestSuite()
    for filename in glob.glob('test_*.py'):
        modname = os.path.splitext(os.path.basename(filename))[0]
        module = __import__(modname)
        allTests.addTest(module.makeSuite())
    return allTests


if __name__ == '__main__':
    sys.path.append("..")

    testSuite = makeSuite()
    unittest.TextTestRunner(verbosity=2).run(testSuite)
