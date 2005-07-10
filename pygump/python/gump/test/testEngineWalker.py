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

import unittest
from pmock import MockTestCase

import os

from gump.engine.walker import Walker

class MockWorkspace:
    def __init__(self):
        self.projects = {}
        self.dependencies = []

class MockDependency:
    def __init__(self, dependee):
        self.dependee = dependee
        
class MockProject:
    def __init__(self, indegree=None):
        if indegree != None:
            self.indegree = indegree

class WalkerTestCase(MockTestCase):
    def setUp(self):
        if not os.path.exists("bla"):
            os.makedirs("bla")
            
        self.log = self.mock()
        self.log.stubs().method("debug")

        w = MockWorkspace()
        w.projects["A"] = MockProject(0)
        w.projects["B"] = MockProject(1)
        w.projects["C"] = MockProject(0)
        w.projects["D"] = MockProject(20)
        w.projects["E"] = MockProject(-5)
        self.w = w
        
        self.walker = Walker(self.log)
    
    def tearDown(self):
        if os.path.exists("bla"):
            import shutil
            shutil.rmtree("bla")

    def test_constructor(self):
        Walker(self.log)
        self.assertRaises(AssertionError,Walker,None)
        self.assertRaises(AssertionError,Walker,"blah")
    
    def test_get_initial_stack(self):
        stack = self.walker._get_initial_stack(self.w)
        self.assertEqual(2,len(stack))
        self.assertEqual(self.w.projects["A"],stack[0])
        self.assertEqual(self.w.projects["C"],stack[1])
    
    def test_clear_indegreees(self):
        self.walker._clear_indegrees(self.w)
        self.assert_(not hasattr(self.w.projects["A"], "indegree"))
        self.assert_(not hasattr(self.w.projects["B"], "indegree"))
        self.assert_(not hasattr(self.w.projects["C"], "indegree"))
        self.assert_(not hasattr(self.w.projects["D"], "indegree"))
        self.assert_(not hasattr(self.w.projects["E"], "indegree"))

    def test_set_indegrees(self):
        w = MockWorkspace()
        w.projects["A"] = MockProject(10)
        w.projects["B"] = MockProject(100)
        w.dependencies.append(MockDependency(w.projects["B"]))
        w.projects["C"] = MockProject(1)
        w.projects["D"] = MockProject(4)
        w.dependencies.append(MockDependency(w.projects["D"]))
        w.dependencies.append(MockDependency(w.projects["D"]))
        w.dependencies.append(MockDependency(w.projects["D"]))
        w.projects["E"] = MockProject(0)
        w.dependencies.append(MockDependency(w.projects["E"]))
        
        self.walker._set_indegrees(w)
        self.assertEqual(0,w.projects["A"].indegree)
        self.assertEqual(1,w.projects["B"].indegree)
        self.assertEqual(0,w.projects["C"].indegree)
        self.assertEqual(3,w.projects["D"].indegree)
        self.assertEqual(1,w.projects["E"].indegree)

    def test_topsort_projects(self):
        # we just use the real model elements here out of laziness.
        # this stuff is properly tested in the model testcase anyway.
        # oh well.
        #
        # TODO: test this a lot more extensively!
        from gump.model import Workspace
        from gump.model import Repository
        from gump.model import Module
        from gump.model import Project
        from gump.model import Dependency
        
        w = Workspace("ws", "bla")
        r = Repository(w,"repo")
        m = Module(r,"mod")
        
        A = Project(m,"A")
        B = Project(m,"B")
        C = Project(m,"C")
        D = Project(m,"D")
        E = Project(m,"E")
        m.add_project(A)
        m.add_project(B)
        m.add_project(C)
        m.add_project(D)
        m.add_project(E)
        
        d1 = Dependency(A,B)
        B.add_dependency(d1)
        d2 = Dependency(A,D)
        D.add_dependency(d2)
        d3 = Dependency(B,D)
        D.add_dependency(d3)
        d4 = Dependency(C,D)
        D.add_dependency(d4)
        d5 = Dependency(D,E)
        E.add_dependency(d5)
        
        list = self.walker._topsort_projects(w)
        self.assert_(list[0] == A or list[0] == C)
        self.assert_(list[1] == C or list[1] == A)
        self.assertEqual(B,list[2])
        self.assertEqual(D,list[3])
        self.assertEqual(E,list[4])
