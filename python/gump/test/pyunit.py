#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    This module contains information on unit testing
"""
import os
import sys
from types import NoneType, StringType, TypeType, MethodType
import types
import logging

from gump import log
import gump.config
from gump.utils import createOrderedList,printSeparator,formatException

from fnmatch import fnmatch    

class Testable:       
    def __init__(self):
        pass
        
    def raiseIssue(self, stuff):
        message=''
        for s in stuff:
            message += '['
            message += str(s)
            message += '] '
            
        raise RuntimeError, message
        
    def assertNotNone(self,message,object):        
        if isinstance(object,NoneType):
            self.raiseIssue(['Ought NOT be None', message, object])
            
    def assertNonZero(self,message,object):
        self.assertNotNone(message,object)
        if not object:
            self.raiseIssue(['Ought evaluate to non-zero', message, object])
            
    def assertEqual(self,message,object1,object2):
        if not object1 == object2:
            self.raiseIssue(['Ought evaluate as equal', message, object1, object2])
            
    def assertGreater(self,message,object1,object2):
        if not object1 > object2:
            self.raiseIssue(['Ought evaluate as greater', message, object1, object2])
            
    def assertNotEqual(self,message,object1,object2):
        if object1 == object2:
            self.raiseIssue(['Ought NOT evaluate as equal', message, object1, object2])
            
    def assertTrue(self,message,object):
        if not object:
            self.raiseIssue(['Ought evaluate as true', message, object])
            
    def assertFalse(self,message,object):
        if object:
            self.raiseIssue(['Ought evaluate as false', message, object])
            
    def assertInString(self,message,substr,str):
        if -1 == str.find(substr):
            self.raiseIssue(['Ought evaluate as in', message, substr, str])
            
    def assertIn(self,message,object,sequence):
        if not object in sequence:
            self.raiseIssue(['Ought evaluate as in', message, object, sequence])
            
    def assertSubstring(self,message,subString,mainString):
        if -1 == mainString.find(subString):
            self.raiseIssue(['Ought evaluate as a substring', \
                message, subString, mainString, mainString.find(subString)])
            
    def assertNotEmpty(self,message,sequence):
        if not sequence or not len(sequence) > 0:
            self.raiseIssue(['Ought NOT evaluate as empty', message, sequence])
            
    def assertNotIn(self,message,object,sequence):
        if object in sequence:
            self.raiseIssue(['Ought NOT evaluate as in', message, object, sequence])

    def assertNotSubstring(self,message,subString,mainString):
        if not -1 == mainString.find(subString):
            self.raiseIssue(['Ought NOT evaluate as a substring', \
                    message, subString, mainString, mainString.find(subString)])            
    
    def assertLengthAbove(self,message,object,length):
        if not len(object) >= length:
            self.raiseIssue(['Ought be longer than', message, object, length])
    
    def assertAt(self,message,object,sequence,posn):
        self.assertLengthAbove(message,sequence,posn+1)        
        self.assertEqual(message,object,sequence[posn] )
            
    def assertString(self,message,object):
        if not type(object) == types.StringType:
            self.raiseIssue(['Ought be a String type', message, object, type(object)])
            
    def assertNonZeroString(self,message,object):
        self.assertNonZero(message,object)
        self.assertString(message,object)
        
class Problem:
    def __init__(self,suite,test,error=None):
        self.suite=suite
        self.test=test
        self.error=error
        
    def __str__(self):
        return self.suite.getName() + ':' + self.test + ':' + self.error
            
class UnitTestSuite(Testable):
    def __init__(self,name=None):
        Testable.__init__(self)
        if name:
            self.name=name
        else:
            self.name=self.__class__.__name__
        self.depends=[]
        self.fullDepends=[]
            
    def addDependency(self,suite):
        self.depends.append(suite)
    
    def getFullDepends(self,visited=None):        
        # Cached already
        if self.fullDepends:
            return self.fullDepends

        if not visited: visited=[]
        if self in visited: return []
        visited.append(self)        
        
        # Calculate
        for suite in self.depends:
            for dependSuite in self.fullDepends(visited):
                if not dependSuite in self.fullDepends:
                    self.fullDepends.append(dependSuite)
        
        # Return complete tree
        return self.fullDepends
        
    def isDependentUpon(self,suite):
        return suite in self.getFullDepends()
        
    def __cmp__(self, other):
        if self.isDependentUpon(other): return 1
        if other.isDependentUpon(self): return -1
        return 0
        
    def getName(self):
        return self.name
        
    def performTests(self,patterns=None):
    
        tests=[]
        results=[]
        
        # log.setLevel(logging.DEBUG ) 
                
        # Give a place to work in..
        if not os.path.exists('./test'): os.mkdir('./test')
        
        # iterate over this suites properties
        for name in self.__class__.__dict__:
            if name.startswith('__') and name.endswith('__'): continue
            test=getattr(self,name)            
            # avoid nulls, metadata, and methods other than test*
            if not test: continue
            if isinstance(test,types.TypeType): continue
            if not isinstance(test,types.MethodType): continue
            if not callable(test): continue
            if not name.startswith('test'): continue
            
            # If arguments, they are patterns to match
            if patterns:
                for pattern in patterns:    
                    try:
                        if pattern=="all": pattern='*'
                        if fnmatch(name,pattern): break         
                    except Exception, detail:
                        log.error('Failed to regexp: ' + pattern + '. Details: ' + str(detail))
                        continue
                else:
                    # no match, advance to the next name
                    continue
                
            # Store to perform
            tests.append(test)
        
        if tests:
            if hasattr(self,'suiteSetUp'):
                self.suiteSetUp()
    
            for test in tests:
                # Call the test...
                try:
                    log.info('Perform [' + self.getName() + '::' + \
                        str(test) + ']')
                        
                    if hasattr(self,'setUp'):
                        self.setUp()
    
                    test()                
                
                    if hasattr(self,'tearDown'):
                        self.tearDown()
        
                except Exception, details:
                    log.error('Failed')    
                    
                    # Log the traceback    
                    import traceback
                    ei = sys.exc_info()
                    message=formatException(ei)
                    del ei                
                    
                    # Record the problem
                    results.append(Problem(self,name,message))
        
            if hasattr(self,'suiteTearDown'):
                self.suiteTearDown()
    
        return (len(tests), results)

      
class TestRunner:
    def __init__(self):
        self.suites=[]
        
    def addSuite(self,suite):
        self.suites.append(suite)
        
    def run(self,args):
        # Sort to resolve dependency order
        runOrder=createOrderedList(self.suites)
        
        testsRun=0
        problems=[]
        
        # Perform the tests
        for suite in runOrder:
            try:
                (runs, results) = suite.performTests(args)
                testsRun += runs
                problems += results
            except Exception, details:
                log.error('Failed')
                import traceback
                ei = sys.exc_info()
                message=formatException(ei)
                del ei    
                problems.append(Problem(suite,'performTests',message)) 
           
        printSeparator()
        
        log.info('Performed [' + `testsRun` + '] tests with [' + `len(problems)` + '] issues.')
        
        for problem in problems:
            log.error('PROBLEM: ' + str(problem))
            
        if not problems:
            log.info('No Problems Detected')
        
        if problems:   sys.exit(1)
        sys.exit(0)
                    
if __name__=='__main__':
    
    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)
    
    runner=TestRunner()
    
    #:TODO: Figure out Python search/introspection to find these...
    
    from gump.test.sync import SyncTestSuite
    runner.addSuite(SyncTestSuite())

    from gump.test.utils import UtilsTestSuite  
    runner.addSuite(UtilsTestSuite())
    
    from gump.test.model import ModelTestSuite  
    runner.addSuite(ModelTestSuite())
    
    from gump.test.stats import StatsTestSuite  
    runner.addSuite(StatsTestSuite())
    
    from gump.test.documenter import DocumenterTestSuite  
    runner.addSuite(DocumenterTestSuite())
    
    from gump.test.updater import UpdaterTestSuite  
    runner.addSuite(UpdaterTestSuite())
    
    from gump.test.syndicator import SyndicatorTestSuite  
    runner.addSuite(SyndicatorTestSuite())
    
    from gump.test.maven import MavenTestSuite  
    runner.addSuite(MavenTestSuite())
    
    from gump.test.xref import XRefTestSuite  
    runner.addSuite(XRefTestSuite())
    
    from gump.test.tools import ToolsTestSuite  
    runner.addSuite(ToolsTestSuite())
    
    from gump.test.tools import ToolsTestSuite  
    runner.addSuite(ToolsTestSuite())
    
    from gump.test.nagging import NaggingTestSuite  
    runner.addSuite(NaggingTestSuite())
    
    from gump.test.resulting import ResultingTestSuite  
    runner.addSuite(ResultingTestSuite())
    
    from gump.test.resolving import ResolvingTestSuite  
    runner.addSuite(ResolvingTestSuite())
    
    from gump.test.unicode import UnicodeTestSuite  
    runner.addSuite(UnicodeTestSuite())
    
    from gump.test.thomas import EngineTestSuite  
    runner.addSuite(EngineTestSuite())
    
    # Any args are pattern matches
    patterns=list(sys.argv)
    del patterns[0:1]
    
    # Perform the tests...
    runner.run(patterns)
    
    
