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
from unittest import TestCase

from gump.test.mockobjects import *

from gump.actor.dynagumper import *

mock = MockObjects()

class DynagumperTestCase(TestCase):
    def setUp(self):
        self.dynagumper = Dynagumper(mock.run,mock.database,log=mock.log)
    
    def testEnsureThisHostIsInDatabase(self):
        #TODO actual tests
        self.dynagumper.ensureThisHostIsInDatabase()

    def testProcessOtherEvent(self):
        #TODO
        self.dynagumper.processOtherEvent("blah")
    
    def testProcessWorkSpace(self):
        #TODO
        self.dynagumper.processWorkspace()
    
    def testProcessModule(self):
        #TODO
        self.dynagumper.processModule("blah")
    
    def testProcessProject(self):
        #TODO
        self.dynagumper.processProject("blah")

# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(DynagumperTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
