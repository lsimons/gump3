#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import unittest
from pmock import *

from gump.plugins.dynagumper import Dynagumper

from main import _Logger

class DynagumperTestCase(MockTestCase):
    def setUp(self):
        self.log = self.mock()
        self.log.stubs().method("debug")
        self.log.stubs().method("info")
        self.log.stubs().method("warning")
        self.log.stubs().method("error")
        self.log.stubs().method("critical")
        self.log.stubs().method("log")
        self.log.stubs().method("exception")
        self.log.stubs().method("close")
        self.db = self.mock()
    
    def test_storeHost(self):
        #TODO actual tests
        db = self.mock()
        db.expects(at_least_once()).method("execute").will(return_value((0,None)))
        dynagumper = Dynagumper(db,self.log)
        dynagumper.storeHost()

    def test_visit_workspace(self):
        #TODO
        class w:
          def __init__(self, n, d):
            self.name = n
            self.description = d
            
        wi = w("blah", "blah blah")
        db = self.mock()
        db.expects(once()).method("execute").will(raise_exception(RuntimeError('bla')))
        dynagumper = Dynagumper(db,self.log)
        self.assertRaises(RuntimeError, dynagumper.visit_workspace, wi)
    
    def test_visit_module(self):
        #TODO
        class m:
          def __init__(self, n, d, u):
            self.name = n
            self.description = d
            self.url = u
            
        mi = m("blah", "blah blah", "http://example.com")
        dynagumper = Dynagumper(self.db,self.log)
        db = self.mock()
        db.expects(once()).method("execute").will(raise_exception(RuntimeError('bla')))
        dynagumper = Dynagumper(db,self.log)
        self.assertRaises(RuntimeError, dynagumper.visit_module, mi)
    
    def test_visit_project(self):
        #TODO
        db = self.mock()
        db.expects(once()).method("execute").will(raise_exception(RuntimeError('bla')))
        dynagumper = Dynagumper(db,self.log)
        self.project = self.mock()
        self.project.name = "blah"
        self.project.startdate = "21 June 2005"
        self.project.enddate = "22 June 2005"
        
        self.assertRaises(RuntimeError, dynagumper.visit_project, self.project)
