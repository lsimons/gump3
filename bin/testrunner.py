#!/usr/bin/env python2.3
"""testrunner - a Zope test suite utility.

The testrunner utility is used to execute PyUnit test suites. This utility
should be run from the root of your Zope source directory. It will set up the
correct python path environment based on your source directory so that
test suites can import Zope modules in a way that is fairly independent of
the location of the test suite. It does *not* import the Zope package, so
a test thats depend on dynamic aspects of the Zope environment (such as
SOFTWARE_HOME being defined) may need to 'import Zope' as a part of the
test suite.

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
-----
This version of testrunner.py supports INSTANCE_HOME installations of Zope.

(c) 2002-2004, Stefan H. Holek, stefan@epy.co.at
-----
Copyright (c) 2004 Zope Corporation and Contributors.All Rights Reserved.This software is subject to the provisions of the Zope Public License,Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIEDWARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIEDWARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESSFOR A PARTICULAR PURPOSE. 
"""

__version__ = '0.4.0'

import getopt
import imp
import os
import sys
import time
import traceback
import unittest
from functools import reduce

VERBOSE = 2


class TestRunner:
    """Test suite runner"""

    def __init__(self, path, verbosity, mega_suite, verbose_on_error,
                 zope_home='', instance_home='', detect_instance_home=0, 
                 unstale_instance_home=0):
        self.basepath = path
        self.verbosity = verbosity
        self.verbose_on_error = verbose_on_error
        self.results = []
        self.mega_suite = mega_suite
        # initialize python path
        pjoin = os.path.join
        if zope_home:
            if sys.platform == 'win32':
                newpaths = [pjoin(zope_home, 'lib', 'python'),
                            pjoin(zope_home, 'bin', 'lib'),
                            pjoin(zope_home, 'bin', 'lib', 'plat-win'),
                            pjoin(zope_home, 'bin', 'lib', 'win32'),
                            pjoin(zope_home, 'bin', 'lib', 'win32', 'lib'),
                            zope_home]
            else:
                newpaths = [pjoin(zope_home, 'lib', 'python'),
                            zope_home]
            sys.path[:0] = newpaths
        # initialize instance home
        if instance_home:
            self.addInstanceHome(instance_home)
            setconfig(instancehome=instance_home)
            self.detect_instance_home = 0
            self.unstale_instance_home = 0
        else:
            self.detect_instance_home = detect_instance_home
            self.unstale_instance_home = unstale_instance_home

    def detectInstanceHome(self):
        """Tries to detect whether we run in an INSTANCE_HOME instance."""
        # Note: SOFTWARE_HOME is set by main() below, even for Zope 2.7 
        software_home = os.environ.get('SOFTWARE_HOME')
        working_dir = realpath(os.getcwd())
        if software_home and not working_dir.startswith(software_home): 
            # Search upwards for a 'Products' directory
            p = d = working_dir
            while d:
                if os.path.isdir(os.path.join(p, 'Products')):
                    return p
                p, d = os.path.split(p)
        return None

    def addInstanceHome(self, instpath):
        """Extends the respective paths to include instance directories."""
        import Products
        # Add 'Products' to Products.__path__
        products = os.path.join(instpath, 'Products')
        if os.path.isdir(products) and products not in Products.__path__:
            if self.verbosity > 1:
                self.report("Adding %s to products path." % products)
            Products.__path__.insert(0, products)
        # Add 'lib/python' to sys.path
        libpython = os.path.join(instpath, 'lib', 'python')
        if os.path.isdir(libpython) and libpython not in sys.path:
            if self.verbosity > 1:
                self.report("Adding %s to sys.path." % libpython)
            sys.path.insert(0, libpython)

    def beforeImportSuite(self):
        """Called before a test suite is imported from a module by
           getSuiteFromFile()."""
        if self.detect_instance_home:
            instpath = self.detectInstanceHome()
            if instpath is not None:
                self.addInstanceHome(instpath)
                self.detect_instance_home = 0
                if getconfig('testinghome'):
                    setconfig(instancehome=instpath)
                if self.unstale_instance_home:
                    walk_with_symlinks(instpath, remove_stale_bytecode, None)

    def getSuiteFromFile(self, filepath):
        if not os.path.isfile(filepath):
            raise ValueError('%s is not a file' % filepath)
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
        print(message, file=sys.stderr)

    def runAllTests(self):
        """Run all tests found in the current working directory and
           all subdirectories."""
        self.runPath(self.basepath)

    def listTestableNames(self, pathname):
        """Return a list of the names to be traversed to build tests."""
        names = os.listdir(pathname)
        for ignore in ('build', 'build-base', 'test_all.py'):
            if ignore in names:
                names.remove(ignore)
        if '.testinfo' in names:  # allow local control
            f = open(os.path.join(pathname, '.testinfo'))
            lines = [_f for _f in f.readlines() if _f]
            lines = [x[-1]=='\n' and x[:-1] or x for x in lines]
            names = [x for x in lines if x and x[0] != '#']
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
        if "verbose_on_error" in list(kw.keys()):
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
        if "verbose_on_error" in list(kw.keys()):
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


def getconfig(key):
    '''Reads a value from Zope configuration.'''
    try:
        import App.config
    except ImportError:
        pass
    else:
        config = App.config.getConfiguration()
        return getattr(config, key, None)


def setconfig(**kw):
    '''Updates Zope configuration'''
    try:
        import App.config
    except ImportError:
        pass
    else:
        config = App.config.getConfiguration()
        for key, value in list(kw.items()):
            setattr(config, key, value)
        App.config.setConfiguration(config)


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
    names = list(map(os.path.normcase, names))
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print("Removing stale bytecode file", fullname, end=' ', file=sys.stderr)
                try:
                    os.unlink(fullname)
                except (OSError, IOError) as e:
                    print(' -->  %s (errno %d)' % (e.strerror, e.errno), file=sys.stderr)
                else:
                    print(file=sys.stderr)


def main(args):
    usage_msg = """Usage: python testrunner.py options

    If run without options, testrunner will display this usage
    message. If you want to run all test suites found in all
    subdirectories of the current working directory, use the
    -a option.

    options:

       -a
          Run all tests found in all subdirectories of the current
          working directory.

       -m
          Run all tests in a single, giant suite (consolidates error
          reporting).  [default]

       -M
          Run each test file's suite separately (noisier output, may
          help in isolating global effects later).

       -p
          Add 'lib/python' to the Python search path.  [default]

       -P
          *Don't* add 'lib/python' to the Python search path.

       -k 
          Remove stale bytecode from ZOPE_HOME and INSTANCE_HOME.
          Highly recommended after e.g. 'cvs update'.

       -K
          *Don't* remove stale bytecode.  [default]

       -i 
          Try to auto-detect INSTANCE_HOME installations.  This usually
          works fine but may fail if your sandbox contains symbolic 
          links.

       -I instpath
          Use the specified path as INSTANCE_HOME.  If auto-detection
          fails or is not appropriate for your setup, you can use this
          flag to specify the instance home directory.

       -C filepath
          Use the specified config file (zope.conf) to setup the test
          instance.  Takes precedence over -i and -I.  [experimental]

       -d dirpath
          Run all tests found in the directory specified by dirpath,
          and recursively in all its subdirectories. The dirpath
          should be a full system path.

       -f filepath
          Run the test suite found in the file specified.  The filepath
          should be a fully qualified path to the file to be run.

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

       -h
          Display usage information.
    """

    pathname = None
    filename = None
    test_all = 0
    verbosity = VERBOSE
    mega_suite = 1
    set_python_path = 1
    timed = 0
    verbose_on_error = 0
    zope_config = ''
    instance_home = ''
    detect_instance_home = 0
    unstale_zope_home = 0
    unstale_instance_home = 0

    try:
        options, arg = getopt.getopt(args, 'aempPhd:f:v:qMo:t:iI:kKC:')
    except getopt.GetoptError as e:
        err_exit(e.msg)
    
    if not options:
        err_exit(usage_msg)
    for name, value in options:
        if name == '-a':
            test_all = 1
        elif name == '-m':
            mega_suite = 1
        elif name == '-M':
            mega_suite = 0
        elif name == '-p':
            set_python_path = 1
        elif name == '-P':
            set_python_path = 0
        elif name == '-i':
            detect_instance_home = 1
        elif name == '-I':
            instance_home = value.strip()
        elif name == '-d':
            pathname = value.strip()
        elif name == '-f':
            filename = value.strip()
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
        elif name == '-o':
            f = open(value.strip(), 'w')
            sys.stderr = f
        elif name == '-k':
            unstale_zope_home = 1
            unstale_instance_home = 1
        elif name == '-K':
            unstale_zope_home = 0
            unstale_instance_home = 0
        elif name == '-C':
            zope_config = value.strip()
        else:
            err_exit(usage_msg)

    if not (test_all or pathname or filename):
        err_exit('must specify one of: -a -d -f')

    # testrunner.py lives in ZOPE_HOME/utilities (or ZOPE_HOME/bin)
    script = sys.argv[0]
    script_dir = os.path.dirname(realpath(script))
    zope_home = os.path.dirname(script_dir)
    if unstale_zope_home:
        walk_with_symlinks(zope_home, remove_stale_bytecode, None)

    software_home = os.path.join(zope_home, 'lib', 'python')
    os.environ['SOFTWARE_HOME'] = software_home

    if zope_config:
        # Use instancehome from config
        instance_home = ''
        detect_instancehome = 0
    else:
        if instance_home:
            instance_home = realpath(instance_home)
            detect_instance_home = 0
            if unstale_instance_home:
                walk_with_symlinks(instance_home, remove_stale_bytecode, None)

    if not set_python_path:
        zope_home = ''

    if timed:
        testrunner = TestTimer(realpath(os.getcwd()), verbosity, mega_suite,
                               verbose_on_error, zope_home, instance_home, 
                               detect_instance_home, unstale_instance_home)
    else:
        testrunner = TestRunner(realpath(os.getcwd()), verbosity, mega_suite,
                                verbose_on_error, zope_home, instance_home, 
                                detect_instance_home, unstale_instance_home)

    if zope_config:
        zope_config = realpath(zope_config)
        if verbosity > 0:
            print('Parsing', zope_config, file=sys.stderr) 
        import Zope
        Zope.configure(zope_config)
        # Ignore softwarehome from config
        setconfig(softwarehome=software_home)
        if unstale_instance_home:
            walk_with_symlinks(getconfig('instancehome'), remove_stale_bytecode, None)

    try:
        # Try to set up the testing environment (esp. INSTANCE_HOME,
        # so we use the right custom_zodb.py.)
        import Testing
    except ImportError:
        pass

    if test_all:
        testrunner.runAllTests()
    elif pathname:
        testrunner.runPath(realpath(pathname))
    elif filename:
        testrunner.runFile(realpath(filename))

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
