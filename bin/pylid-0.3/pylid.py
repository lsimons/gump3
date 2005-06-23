#!/usr/bin/env python2.3
"""
pylid v0.3

Copyright (c) 2002, Nullcube Pty Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
*   Neither the name of Nullcube nor the names of its contributors may be used to
    endorse or promote products derived from this software without specific prior
    written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import sys, parser, token, symbol, copy, getopt, unittest, os, fnmatch, os.path, time, glob, trace

UNIT_TEST_FILE_NAME_GLOB = 'test*.py' # 'test_*.py'

def isPathContained(outer, inner):
    """
       Does inner lie "within" outer?
       Outer has to be an absolute path!
    """
    return (os.path.abspath(inner)[:len(outer)] == outer)


def summariseList(lst):
    """
        Takes a list of numbers, and returns a summary.
        Eg. [1, 2, 3, 4, 9] -> [(1, 4), 9]
            [1, 2, 3, 7, 8, 9] -> [(1, 3), (7, 9)]
    """
    if len(lst) < 2:
        return lst

    ranges = []
    start = 0
    for i in range(1, len(lst)):
        if (lst[i] - lst[i-1]) > 1:
            if (i-1) == start:
                start = i
                ranges.append(lst[i-1])
            else:
                ranges.append((lst[start], lst[i-1]))
                start = i
    if lst[start] == lst[i]:
        ranges.append(lst[i])
    else:
        ranges.append((lst[start], lst[i]))
    return ranges


class GlobDirectoryWalker:
    """
    A forward iterator that traverses files in a directory tree.
    """
    def __init__(self, directory, pattern='*'):
        self.stack = [directory]
        self.pattern = pattern
        self.files = []
        self.index = 0

    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                if fnmatch.fnmatch(file, self.pattern):
                    return fullname


class Coverage:
    """
        Analyse code coverage.
    """
    def __init__(self, coveragePath, excludeList=[]):
        self.coveragePath = os.path.abspath(coveragePath)
        self.excludeList = [os.path.abspath(x) for x in excludeList]
        # Keys are filenames, values are dictionaries of line numbers.
        self.linesRun = {}
        self.statementsRun = {}
        self.allStatements = {}
        # Keys are filenames, values are lists of lines for statements not covered.
        self.statementsNotRun = {}
        # Data gathered by the _trace method
        self._traceData = {}
        # Is our calculated coverage up to date?
        self.coverageUpToDate = 0

    def _trace(self, frame, event, arg):
        """
            Called for every code event. We extract and take note of the
            filename and line number.
        """
        self._traceData[(os.path.abspath(frame.f_code.co_filename), frame.f_lineno)] = 1
        return self._trace

    def _integrateTrace(self):
        for i in self._traceData:
            if (os.path.abspath(i[0])[:len(self.coveragePath)] == self.coveragePath):
                if self.linesRun.has_key(i[0]):
                    self.linesRun[i[0]][i[1]] = 1     
                else:
                    self.linesRun[i[0]] = {i[1]: 1}
        self._traceData = {}

    def start(self):
        sys.settrace(self._trace)

    def stop(self):
        sys.settrace(None)
        self.coverageUpToDate = 0

    def _findTerminal(self, lst):
        """
            Find the first TERMINAL token and return its line number.
        """
        if token.ISTERMINAL(lst[0]):
            return lst[2]
        else:
            return self._findTerminal(lst[1])
            
    def _makeCoverage(self):
        """
            Runs through the list of files, calculates a list of lines that
            weren't covered, and writes the list to self.files["filenames"].
        """
        if not self.coverageUpToDate:
            self._integrateTrace()
            for fileName in self.linesRun.keys():
                # We only want to get the parsed statement list once
                if not self.allStatements.has_key(fileName):
                    for p in self.excludeList:
                        if isPathContained(p, fileName):
                            del self.linesRun[fileName]
                            break
                    else:
                        self.allStatements[fileName] = trace.find_executable_linenos(fileName)
                        self.allStatements[fileName].update(self.linesRun[fileName])

            # Calculate statementsRun
            sr = {}
            for fileName in self.linesRun:
                sr[fileName] = {}
                for i in self.linesRun[fileName]:
                    if self.allStatements[fileName].has_key(i):
                        sr[fileName][i] = 1
            self.statementsRun = sr

            # Calculate statementsNotRun
            snr = {}
            for fileName in self.allStatements:
                snr[fileName] = []
                for i in self.allStatements[fileName]:
                    if not self.statementsRun[fileName].has_key(i):
                        snr[fileName].append(i)
                snr[fileName].sort()
            self.statementsNotRun = snr
            self.coverageUpToDate = 1

    def getStats(self):
        """
            Returns a list of tuples, containing a dictionary of statistics each. 
            [(name, resultDict)...]
        """
        self._makeCoverage()
        allStats = []
        for fileName in self.linesRun:
            statDict = {}
            statDict["allStatements"] = len(self.allStatements[fileName])
            statDict["statementsRun"] = len(self.statementsRun[fileName])
            if statDict["allStatements"]:
                statDict["coverage"] = (float(statDict["statementsRun"])/float(statDict["allStatements"]))*100
            else:
                # Empty file (e.g. empty __init__.py)
                statDict["coverage"] = 100.0
            statDict["ranges"] = summariseList(self.statementsNotRun[fileName])
            allStats.append((fileName, statDict))

        def compare(a, b):
            return cmp(len(self.statementsNotRun[a[0]]), len(self.statementsNotRun[b[0]]))

        allStats.sort(compare)
        return allStats

    def getGlobalStats(self):
        """
            Returns a dictionary of statistics covering all files.
        """
        self._makeCoverage()
        # Overall lines
        statementsRun = 0
        allStatements = 0
        for fileName in self.linesRun:
            statementsRun += len(self.statementsRun[fileName])
            allStatements += len(self.allStatements[fileName])
        if allStatements == 0:
            perc = 0 
        else:
            perc = ((float(statementsRun)/float(allStatements))*100)

        return {
                    "statementsRun": statementsRun,
                    "allStatements": allStatements,
                    "percentage": perc
                }

    def getAnnotation(self):
        """
            Returns a dictionary with a list of snippets of text. Each snippet
            is an annotated list of un-run lines.
        """
        self._makeCoverage()
        annotations = {}
        for fileName in self.statementsNotRun:
            if self.statementsNotRun[fileName]:
                lines = open(fileName).readlines()
                for i in self.statementsNotRun[fileName]:
                    lines[i-1] = "> " + lines[i-1]
                annotations[fileName] = lines
        return annotations


class Tester:
    def __init__(self, baseDirs, include, exclude):
        """
            Takes the project base directories. These directories are inserted into
            our path so that unit tests can import files/modules from there. 
        """
        # We want to be able to import from the current dir
        self.cov = Coverage(include, exclude)
        for baseDir in baseDirs:
            sys.path.insert(0, baseDir)

        # We also insert the current directory, to make sure we can import
        # source files in our test directory.
        sys.path.insert(0, ".")
        self.suite = unittest.TestSuite()
        self.coverage = 0

    def _addFile(self, path, coverage):
        dirName, fileName = os.path.split(path)
        sys.path.insert(0, dirName)
        modname = os.path.splitext(os.path.basename(fileName))[0]
        if coverage:
            self.cov.start()
        module = __import__(modname)
        if coverage:
            self.cov.stop()
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
        self.suite.addTest(tests)
        del sys.path[0]

    def addPath(self, path, coverage):
        if os.path.isfile(path):
            self._addFile(path, coverage)
        elif os.path.isdir(path):
            for filename in glob.glob(os.path.join(path, UNIT_TEST_FILE_NAME_GLOB)):
                self._addFile(filename, coverage)
        else:
            # We now assume that it's a module
            if coverage:
                self.cov.start()
            tests = unittest.defaultTestLoader.loadTestsFromName(path)
            if coverage:
                self.cov.stop()
            self.suite.addTest(tests)

    def coverageRun(self, verbosity=0):
        """
            "include" is a directory that should be included in the coverage analysis.
            "exclude" is a set of directories that should be explicitly excluded. 
        """
        self.cov.start()
        unittest.TextTestRunner(verbosity=verbosity).run(self.suite)
        self.cov.stop()

    def run(self, verbosity=0):
        unittest.TextTestRunner(verbosity=verbosity).run(self.suite)

    def debug(self):
        self.suite.debug()

    def coverageStats(self):
        stats = self.cov.getStats()
        print "[run ] [tot ] [percent]"
        print "======================="
        for i in stats:
            print "[%-4s] [%-4s] [%-6.5s%%]:     %s  " % (    i[1]["statementsRun"],
                                                              i[1]["allStatements"],
                                                              i[1]["coverage"],
                                                              i[0])
            if i[1]["ranges"]:
                print "                            ",
                for j in i[1]["ranges"]:
                    try:
                        print "[%s...%s] "%(j[0], j[1]),
                    except:
                        print "%s "%(j),
                print

    def coverageSummary(self):
        x = self.cov.getGlobalStats()
        print
        print "Summary:"
        print "\t\tStatements Total: %s"%x["allStatements"]
        print "\t\tStatements Run:   %s"%x["statementsRun"]
        print "\t\tPercentage:       %.5s%%"%x["percentage"]

    def _page(self, data):
        if os.environ.has_key("PAGER"):
            cmd = os.environ["PAGER"]
            pipe = os.popen(cmd, 'w')
            try:
                pipe.write(data)
                pipe.close()
            except IOError:
                pass # Ignore broken pipes caused by quitting the pager program.
        else:
            print "Please define a 'PAGER' environment variable."

    def pageAnnotations(self):
        ann = self.cov.getAnnotation()
        for i in ann:
            print "View annotation for %s? "%i,
            ans = raw_input()
            if ans in ["y", "Y"]:
                self._page("".join(ann[i]))


def main():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser(version="%prog 0.3")
    parser.add_option("-a", "--annotate",
                      action="store_true", dest="annotate",
                      help="Page annotations")
    parser.add_option("-c", "--clear",
                      action="store_true", dest="clear",
                      help="Clear all .pyc and .pyo files in the project base and included paths")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help="Debug run - do not catch exceptions")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet",
                      help="Quiet")
    parser.add_option("-s", "--stats",
                      action="store_true", dest="stats",
                      help="Give coverage stats")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help="Verbose.")

    group = OptionGroup(parser, "Controlling Coverage Paths",
                        "If a project is structured correctly, these options will rarely be required.")
    group.add_option("-b", "--base",
                      action="store", type="string", dest="base", default="..", metavar="DIR",
                      help='Project base directories, seperated by colons. (Default: "..")')
    group.add_option("-e", "--exclude",
                      action="append", type="string", dest="exclude", metavar="DIR",
                      help='Exclude path from coverage analysis. Can be passed multiple times. (Default: ".")')
    group.add_option("-i", "--include",
                      action="store", type="string", dest="include", default="..", metavar="DIR",
                      help='Include path for analysis. (Default: "..")')

    parser.add_option_group(group)

    (options, args) = parser.parse_args()


    if not options.exclude:
        options.exclude = ["."]

    verbosity = 1
    if options.quiet:
        verbosity -= 1
    if options.verbose:
        verbosity += 1

    if options.clear:
        for filename in GlobDirectoryWalker(options.include, '*.pyc'):
            os.remove(filename)
        for basedir in options.base.split(':'):
            for filename in GlobDirectoryWalker(basedir, '*.pyc'):
                os.remove(filename)
        for filename in GlobDirectoryWalker(options.include, '*.pyo'):
            os.remove(filename)
        for basedir in options.base.split(':'):
            for filename in GlobDirectoryWalker(basedir, '*.pyo'):
                os.remove(filename)

    # Do the actual run
    t = Tester(options.base.split(':'), options.include, options.exclude)

    dostats = options.stats or options.annotate

    if args:
        for i in args:
            t.addPath(i, dostats)
    else:
        t.addPath(".", dostats)

    if options.debug:
        t.debug()
    elif dostats:
        t.coverageRun(verbosity=verbosity)
    else:
        t.run(verbosity)

    # Report the results
    if options.stats:
        print
        print 
        print "                    Coverage"
        print "                    ========"
        print
        t.coverageStats()
        t.coverageSummary()

    if options.annotate:
        t.pageAnnotations()

if __name__ == "__main__":
    main()
