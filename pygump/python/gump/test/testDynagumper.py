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

from gump.test.mockobjects import *
from gump.plugins.dynagumper import Dynagumper
from gump.model import Project

mock = MockObjects()

class DynagumperTestCase(unittest.TestCase):
    def setUp(self):
        self.dynagumper = Dynagumper(mock.database,mock.log)
        self.project = Project("blah", "blah")
        self.project.startdate = "21 June 2005"
        self.project.enddate = "22 June 2005"
    
    def testEnsureThisHostIsInDatabase(self):
        #TODO actual tests
        self.dynagumper.ensureThisHostIsInDatabase()

    def testVisitWorkSpace(self):
        #TODO
        self.dynagumper.visit_workspace("blah")
    
    def testVisitModule(self):
        #TODO
        self.dynagumper.visit_module("blah")
    
    def testVisitProject(self):
        #TODO
        self.dynagumper.visit_project(self.project)

# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(DynagumperTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
