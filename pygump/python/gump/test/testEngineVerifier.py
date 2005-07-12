#!/usr/bin/env python

# Copyright 2005 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

"""Tests for gump.engine.verifier"""

import unittest
from pmock import *

from gump.engine.verifier import VerificationError
from gump.engine.verifier import CyclicDependencyError
from gump.engine.verifier import print_cyclic_trace
from gump.engine.verifier import AbstractErrorHandler
from gump.engine.verifier import LoggingErrorHandler
from gump.engine.verifier import Verifier

class Project:
    def __init__(self, name):
        self.name = name
        self.dependencies = []
    
    def __str__(self):
        return "project:%s" % self.name

class Relationship:
    def __init__(self, project):
        self.dependency = project

    def __rel__(self):
        return "relationship:dependency=%s" % self.dependency

class MyError(Exception):
    pass
    
counter = 0
def p():
    global counter
    counter = counter + 1
    return Project("project_%s" % counter)
        
def r(p):
    return Relationship(p)

class EngineVerifierTestCase(MockTestCase):
    def setUp(self):
        self.walker = self.mock()
        self.walker.stubs().method("walk")
        self.handler = self.mock()
        self.handler.stubs().method("_handleError")
    
    def test_VerificationError(self):
        e = VerificationError()
        
    def test_CyclicDependencyError(self):
        e = CyclicDependencyError()
        
    def test_print_cyclic_trace(self):
        def handler(msg):
            pass
        
        cycles = []
        p1 = p()
        p2 = p()
        cycles.append([p1, p(), p(), p1])
        cycles.append([p2, p(), p(), p(), p(), p(), p2])
        print_cyclic_trace(cycles, handler)
        
        
    def test_AbstractErrorHandler(self):
        called = []
        def handleError(called=called):
            called.append(1)
        
        e = AbstractErrorHandler()
        e.handleError = handleError
        e._handleError()
        self.failUnless(len(called) == 1)
        
        e = AbstractErrorHandler()
        try:
            raise MyError, "problem"
        except:
            try:
                e._handleError()
                self.fail("Exception swallowed")
            except MyError:
                pass

            
    def test_LoggingErrorHandler(self):
        log = self.mock()
        log.expects(at_least_once()).method("error")
        
        e = LoggingErrorHandler(log)
        cycles = []
        cycle = []
        cycle.append(Project("a"))
        cycle.append(Project("b"))
        cycles.append(cycle)
        
        try:
            raise CyclicDependencyError, cycles
        except:
            e._handleError()

        try:
            raise MyError, "problem"
        except:
            try:
                e._handleError()
                self.fail("Exception swallowed")
            except MyError:
                pass

    def test_Verifier__init__(self):
        v = Verifier(self.walker, self.handler)
        self.assertEqual(self.walker, v.walker)
        self.assertEqual(self.handler, v.errorHandler)
        self.assertRaises(AssertionError, Verifier, None, self.handler)
        self.assertRaises(AssertionError, Verifier, self.walker, None)
        
    def test_Verifier_verify(self):
        v = Verifier(self.walker, self.handler)
        
        p1 = p()
        p2 = p()
        p3 = p()
        p4 = p()
        p5 = p()
        p6 = p()
        p7 = p()
        p8 = p()
        p9 = p()
        p10 = p()

        p1.dependencies.append(r(p2))
        p1.dependencies.append(r(p3))
        #p1.dependencies.append(r(p4))
        p1.dependencies.append(r(p5))
        p1.dependencies.append(r(p6))

        #p2.dependencies.append(r(p3))
        #p2.dependencies.append(r(p4))
        p2.dependencies.append(r(p5))
        p2.dependencies.append(r(p6))

        #p3.dependencies.append(r(p3))
        p3.dependencies.append(r(p4))
        p3.dependencies.append(r(p5))
        p3.dependencies.append(r(p6))
        #p3.dependencies.append(r(p7))
        p3.dependencies.append(r(p8))
        p3.dependencies.append(r(p9))
        #p3.dependencies.append(r(p10))

        p4.dependencies.append(r(p5))
        p4.dependencies.append(r(p6))
        p4.dependencies.append(r(p7))
        p4.dependencies.append(r(p8))
        p4.dependencies.append(r(p9))
        #p4.dependencies.append(r(p10))

        p7.dependencies.append(r(p8))
        p7.dependencies.append(r(p9))
        p7.dependencies.append(r(p10))

        visited = []
        project = p1
        stack = [p1]
        needle = p1
        cycles = []
        
        # first we test the internal _visit()
        v._visit(project,visited,stack,needle,cycles)
        self.assertEqual(len(cycles), 0)
        
        # introduce a cycle
        p10.dependencies.append(r(p1))
        visited = []
        project = p1
        stack = [p1]
        needle = p1
        cycles = []
        
        v._visit(project,visited,stack,needle,cycles)
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        self.assertEqual(p1,cycle[0])
        self.assertEqual(p3,cycle[1])
        self.assertEqual(p4,cycle[2])
        self.assertEqual(p7,cycle[3])
        self.assertEqual(p10,cycle[4])
        self.assertEqual(p1,cycle[5])

        # introduce more cycles, and more complex ones
        p2.dependencies.append(r(p1))
        p3.dependencies.append(r(p1))
        p2.dependencies.append(r(p3))
        visited = []
        project = p1
        stack = [p1]
        needle = p1
        cycles = []
        
        v._visit(project,visited,stack,needle,cycles)
        self.assertEqual(len(cycles), 5)

        # now test _find_cycles method
        projects = [p1, p2, p3, p4, p7, p10]
        
        # behaviour manually verified as being correct on Jul 12
        #def handler(msg):
            #print msg
        #print_cyclic_trace(v._find_cycles(projects), handler)
        self.assertEqual(len(v._find_cycles(projects)), 18)
        
        # finally, the sugared up verify...
        walker = self.mock()
        # (visited_repositories, visited_modules, visited_projects) = self.walker.walk(workspace, visitor)
        walker.expects(at_least_once()).method("walk").will(return_value((None, None, [p5, p6, p8, p9])))
        
        handler = self.mock()
        handler.expects(once()).method("_handleError").will(raise_exception(CyclicDependencyError))
        
        class Workspace:
            projects = {"p1": p1,
                        "p2": p2,
                        "p3": p3,
                        "p4": p4,
                        "p5": p5,
                        "p6": p6,
                        "p7": p7,
                        "p8": p8,
                        "p9": p9,
                        "p10": p10}
            cycles = []
            unvisited = []
        
        w = Workspace()
        
        v = Verifier(walker, handler)
        self.assertRaises(CyclicDependencyError, v.verify, w)
        self.assertEqual(len(w.cycles), 18)
        self.assertEqual(len(w.unvisited), 6)
        self.assertEqual(len(w.unvisited), 6)
        
        v = Verifier(walker, self.handler)
        w = Workspace()
        w.projects = {"p5": p5,
                        "p6": p6,
                        "p8": p8,
                        "p9": p9}
        v.verify(w)
        self.assertEqual(len(w.cycles), 0)
        self.assertEqual(len(w.unvisited), 0)
