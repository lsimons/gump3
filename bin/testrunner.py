#!/usr/bin/env python2.3
"""testrunner - a Zope test suite utility.

The testrunner utility is used to execute PyUnit test suites.

Testrunner will look for and execute test suites that follow some simple
conventions. Test modules should have a name prefixed with 'test', such as
'testMyModule.py', and test modules are expected to define a module function
named 'test_suite' that returns a TestSuite object. By convention,
we put test modules in a 'tests' sub-package of the package they test.

Testrunner is used to run all checked in test suites before (final) releases
are made, and can be used to quickly run a particular suite or all suites in
a particular directory.

-----
This file was found at http://zope.org/Members/shh/TestRunner. Changes:
    * added Zope license header
    
    * added code coverage reporting switch based on the trace module
      (not functional)
    
    * remove zope-specific path management
-----
(c) 2002-2004, Stefan H. Holek, stefan@epy.co.at
-----
Copyright (c) 2004 Zope Corporation and Contributors.
All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE. 
"""

__version__ = '0.4.1-LSD'

import getopt
import imp
import os
import sys
import time
import traceback
import unittest
import trace
VERBOSE = 2


class TestRunner:
    """Test suite runner"""

    def __init__(self, path, verbosity, mega_suite, verbose_on_error):
        self.basepath = path
        self.verbosity = verbosity
        self.verbose_on_error = verbose_on_error
        self.results = []
        self.mega_suite = mega_suite

    def beforeImportSuite(self):
        """Called before a test suite is imported from a module by
           getSuiteFromFile()."""
        pass

    def getSuiteFromFile(self, filepath):
        if not os.path.isfile(filepath):
            raise ValueError, '%s is not a file' % filepath
        path, filename = os.path.split(filepath)
        name, ext = os.path.splitext(filename)
        file, pathname, desc = imp.find_module(name, [path])
        self.beforeImportSuite()        # NB: Called *before* saving sys.path
        saved_syspath = sys.path[:]
        module = None
        try:
            sys.path.append(path)       # let module find things in its dir
            try:
                module=imp.load_module(name, file, pathname, desc)
            except KeyboardInterrupt:
                raise
            except:
                (tb_t, tb_v, tb_tb) = sys.exc_info()
                self.report("Module %s failed to load\n%s: %s" % (pathname,
                        tb_t, tb_v))
                self.report(''.join(traceback.format_tb(tb_tb)) + '\n')
                del tb_tb
        finally:
            file.close()
            sys.path[:] = saved_syspath
        function=getattr(module, 'test_suite', None)
        if function is None:
            return None
        return function()

    def smellsLikeATest(self, filepath):
        path, name = os.path.split(filepath)
        fname, ext = os.path.splitext(name)

        if (  name[:4] == 'test'
              and name[-3:] == '.py'
              and name != 'testrunner.py'):
            file = open(filepath, 'r')
            lines = file.readlines()
            file.close()
            for line in lines:
                if (line.find('def test_suite(') > -1) or \
                   (line.find('framework(') > -1):
                    return 1
        return 0

    def runSuite(self, suite):
        if suite:
            runner = self.getTestRunner()
            self.results.append(runner.run(suite))
        else:
            self.report('No suitable tests found')

    _runner = None

    def getTestRunner(self):
        if self._runner is None:
            self._runner = self.createTestRunner()
        return self._runner

    def createTestRunner(self):
        return FancyTestRunner(stream=sys.stderr,
                               verbosity=self.verbosity,
                               verbose_on_error=self.verbose_on_error)

    def report(self, message):
        print >>sys.stderr, message

    def listTestableNames(self, pathname):
        """Return a list of the names to be traversed to build tests."""
        names = os.listdir(pathname)
        for ignore in ('build', 'build-base', 'test_all.py'):
            if ignore in names:
                names.remove(ignore)
        if '.testinfo' in names:  # allow local control
            f = open(os.path.join(pathname, '.testinfo'))
            lines = filter(None, f.readlines())
            lines = map(lambda x: x[-1]=='\n' and x[:-1] or x, lines)
            names = filter(lambda x: x and x[0] != '#', lines)
            f.close()
        return names

    def extractSuite(self, pathname):
        """Extract and return the appropriate test suite."""
        if os.path.isdir(pathname):
            suite = unittest.TestSuite()
            for name in self.listTestableNames(pathname):
                fullpath = os.path.join(pathname, name)
                sub_suite = self.extractSuite(fullpath)
                if sub_suite:
                    suite.addTest(sub_suite)
            return suite.countTestCases() and suite or None

        elif self.smellsLikeATest(pathname):
            dirname, name = os.path.split(pathname)
            working_dir = realpath(os.getcwd())
            try:
                if dirname:
                    os.chdir(dirname)
                try:
                    suite = self.getSuiteFromFile(name)
                except KeyboardInterrupt:
                    raise
                except:
                    self.report('No test suite found in file:\n%s\n'
                                % pathname)
                    if self.verbosity > 1:
                        traceback.print_exc()
                    suite = None
            finally:
                os.chdir(working_dir)
            return suite

        else:
            # no test there!
            return None

    def runPath(self, pathname):
        """Run all tests found in the directory named by pathname
           and all subdirectories."""
        if not os.path.isabs(pathname):
            pathname = os.path.join(self.basepath, pathname)

        if self.mega_suite:
            suite = self.extractSuite(pathname)
            self.runSuite(suite)
        else:
            for name in self.listTestableNames(pathname):
                fullpath = os.path.join(pathname, name)
                if os.path.isdir(fullpath):
                    self.runPath(fullpath)
                elif self.smellsLikeATest(fullpath):
                    self.runFile(fullpath)

    def runFile(self, filename):
        """Run the test suite defined by filename."""
        dirname, name = os.path.split(filename)
        working_dir = realpath(os.getcwd())
        if dirname:
            if self.verbosity > 2:
                self.report('*** Changing directory to: %s\n' % dirname)
            os.chdir(dirname)
        self.report('Running: %s' % filename)
        try:
            suite = self.getSuiteFromFile(name)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            suite = None
        if suite is not None:
            os.chdir(working_dir)
            self.runSuite(suite)
        else:
            self.report('No test suite found in file:\n%s\n' % filename)
        if self.verbosity > 2:
            self.report('*** Restoring directory to: %s\n' % working_dir)
        os.chdir(working_dir)


class FancyTestResult(unittest._TextTestResult):
    have_blank_line = 1
    verbose_on_error = 0

    def __init__(self, *args, **kw):
        if "verbose_on_error" in kw.keys():
            self.verbose_on_error = kw["verbose_on_error"]
            del kw["verbose_on_error"]
        unittest._TextTestResult.__init__(self, *args, **kw)

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        if self.showAll:
            self.stream.writeln("ok")
        elif self.dots:
            self.stream.write('.')
            self.have_blank_line = 0

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        if self.showAll:
            if isinstance(err[0], str):
                self.stream.writeln(err[0])
            else:
                self.stream.writeln(excname(err[0]))
        elif self.verbose_on_error:
            if not self.have_blank_line:
                self.stream.writeln()
            self.stream.write(self.getDescription(test) + ": ")
            if isinstance(err[0], str):
                self.stream.writeln(err[0])
            else:
                self.stream.writeln(excname(err[0]))
            self.have_blank_line = 1
        elif self.dots:
            self.stream.write("E")
            self.have_blank_line = 0

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        if self.showAll:
            self.stream.writeln("FAIL")
        elif self.verbose_on_error:
            if not self.have_blank_line:
                self.stream.writeln()
            self.stream.writeln(self.getDescription(test) + ": FAIL")
            self.have_blank_line = 1
        elif self.dots:
            self.stream.write("F")
            self.have_blank_line = 0


def excname(cls):
    if cls.__module__ == "exceptions":
        return cls.__name__
    else:
        return "%s.%s" % (cls.__module__, cls.__name__)


class FancyTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kw):
        if "verbose_on_error" in kw.keys():
            self.verbose_on_error = kw["verbose_on_error"]
            del kw["verbose_on_error"]
        else:
            self.verbose_on_error = 0
        unittest.TextTestRunner.__init__(self, *args, **kw)

    def _makeResult(self):
        return FancyTestResult(self.stream, self.descriptions, self.verbosity,
                               verbose_on_error=self.verbose_on_error)


class TimingTestResult(FancyTestResult):
    def __init__(self, *args, **kw):
        self.timings = []
        FancyTestResult.__init__(self, *args, **kw)

    def startTest(self, test):
        FancyTestResult.startTest(self, test)
        self._t2 = None
        self._t1 = time.time()

    def stopTest(self, test):
        t2 = time.time()
        if self._t2 is not None:
            t2 = self._t2
        t = t2 - self._t1
        self.timings.append((t, str(test)))
        FancyTestResult.stopTest(self, test)

    def addSuccess(self, test):
        self._t2 = time.time()
        FancyTestResult.addSuccess(self, test)

    def addError(self, test, err):
        self._t2 = time.time()
        FancyTestResult.addError(self, test, err)

    def addFailure(self, test, err):
        self._t2 = time.time()
        FancyTestResult.addFailure(self, test, err)


class TimingTestRunner(FancyTestRunner):
    def __init__(self, *args, **kw):
        FancyTestRunner.__init__(self, *args, **kw)
        self.timings = []

    def _makeResult(self):
        r = TimingTestResult(self.stream, self.descriptions, self.verbosity,
                             verbose_on_error=self.verbose_on_error)
        self.timings = r.timings
        return r


class TestTimer(TestRunner):
    def createTestRunner(self):
        return TimingTestRunner(stream=sys.stderr,
                                verbosity=self.verbosity,
                                verbose_on_error=self.verbose_on_error)

    def reportTimes(self, num):
        r = self.getTestRunner()
        r.timings.sort()
        for item in r.timings[-num:]:
            self.report("%.1f %s\n" % item)


def realpath(path):
    try:
        from os.path import realpath
    except ImportError:
        try:
            from App.Common import realpath
        except ImportError:
            realpath = os.path.abspath
    if not path:
        return path
    return realpath(path)


def walk_with_symlinks(path, visit, arg):
    """Like os.path.walk, but follows symlinks on POSIX systems.

    This could theoretically result in an infinite loop, if you create symlink
    cycles in your Zope sandbox, so don't do that.
    """
    try:
        names = os.listdir(path)
    except os.error:
        return
    visit(arg, path, names)
    exceptions = (os.curdir, os.pardir)
    for name in names:
        if name not in exceptions:
            name = os.path.join(path, name)
            if os.path.isdir(name):
                walk_with_symlinks(name, visit, arg)


def remove_stale_bytecode(arg, dirname, names):
    names = map(os.path.normcase, names)
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print >>sys.stderr, "Removing stale bytecode file", fullname,
                try:
                    os.unlink(fullname)
                except (OSError, IOError), e:
                    print >>sys.stderr, ' -->  %s (errno %d)' % (e.strerror, e.errno)
                else:
                    print >>sys.stderr


def main(args):
    usage_msg = """Usage: python testrunner.py -d dir options

    If run without options, testrunner will display this usage
    message.

    options:

       -m
          Run all tests in a single, giant suite (consolidates error
          reporting).  [default]

       -M
          Run each test file's suite separately (noisier output, may
          help in isolating global effects later).

       -d dirpath
          Run all tests found in the directory specified by dirpath,
          and recursively in all its subdirectories. The dirpath
          should be a full system path.

       -v level
          Set the Verbosity level to level.  Newer versions of
          unittest.py allow more options than older ones.  Allowed
          values are:

            0 - Silent
            1 - Quiet (produces a dot for each succesful test)
            2 - Verbose (default - produces a line of output for each test)

       -e
          Modifier to the verbosity level.  This causes errors and
          failures to generate a one-line report instead of an 'E' or 'F'.  
          This can make it easier to work on solving problems while the 
          tests are still running.  This causes the 'silent' mode (-v0) 
          to be less than completely silent.

       -q
          Run tests without producing verbose output.  The tests are
          normally run in verbose mode, which produces a line of
          output for each test that includes the name of the test and
          whether it succeeded.  Running with -q is the same as
          running with -v1.

       -o filename
          Output test results to the specified file rather than
          to stderr.

       -t N
          Report time taken by the most expensive N tests.
    
       -T
          Generate coverage reports. Overrides and ignores -t.

       -h
          Display usage information.
    """

    pathname = None
    verbosity = VERBOSE
    mega_suite = 1
    timed = 0
    coverage = 0
    verbose_on_error = 0

    try:
        options, arg = getopt.getopt(args, 'Temhd:v:qMo:t:kKC:')
    except getopt.GetoptError, e:
        err_exit(e.msg)
    
    if not options:
        err_exit(usage_msg)
    for name, value in options:
        if name == '-m':
            mega_suite = 1
        elif name == '-M':
            mega_suite = 0
        elif name == '-d':
            pathname = value.strip()
        elif name == '-h':
            err_exit(usage_msg, 0)
        elif name == '-e':
            verbose_on_error = 1
        elif name == '-v':
            verbosity = int(value)
        elif name == '-q':
            verbosity = 1
        elif name == '-t':
            timed = int(value)
            assert timed >= 0
        elif name == '-T':
            coverage = 1
        elif name == '-o':
            f = open(value.strip(), 'w')
            sys.stderr = f
        else:
            err_exit(usage_msg)

    if not pathname:
        err_exit('must specify -d')

    if timed:
        testrunner = TestTimer(realpath(os.getcwd()), verbosity, mega_suite,
                               verbose_on_error)
    else:
        testrunner = TestRunner(realpath(os.getcwd()), verbosity, mega_suite,
                                verbose_on_error)

    #if coverage:
    #    cmd = 'testrunner.runPath("%s")' % realpath(pathname)
    #    print "Command to run:", cmd

    #    import trace
    #    t = trace.Trace(count=1, trace=0,
    #                    ignoredirs=[sys.prefix, sys.exec_prefix],
    #                    ignoremods=["testrunner"])
    #    t.runctx(cmd, globals=globals(), locals=vars())
    #    r = t.results()
        #coverdir='%s/pygump/.coverage' % os.environ["GUMP_HOME"]
        #r.write_results(show_missing=True, summary=True, coverdir=coverdir)
    #    r.write_results(show_missing=True, summary=True)
    #else:
    testrunner.runPath(realpath(pathname))

    if timed:
        testrunner.reportTimes(timed)

    ## Report overall errors / failures if there were any
    fails = reduce(lambda x, y: x + len(y.failures), testrunner.results, 0)
    errs  = reduce(lambda x, y: x + len(y.errors), testrunner.results, 0)
    if fails or errs:
        msg = '=' * 70
        msg += "\nOVERALL FAILED ("
        if fails:
            msg += "total failures=%d" % fails
        if errs:
            if fails:
                msg += ", "
            msg += "total errors=%d" % errs
        msg += ")"
        err_exit(msg, 1)

    sys.exit(0)


def err_exit(message, rc=2):
    sys.stderr.write("\n%s\n" % message)
    sys.exit(rc)


if __name__ == '__main__':
    main(sys.argv[1:])
