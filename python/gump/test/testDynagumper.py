#!/usr/bin/env python

# Copyright 2004 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2004 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import unittest
from unittest import TestCase

from gump.test.mockobjects import *

from gump.actor.mysql.dynagumper import *
from gump.core.model.workspace import *


class DynagumperTestCase(TestCase):
    def setUp(self):
        self.workspace = MockWorkspace()
        self.options = MockOptions()
        self.gumpSet = MockGumpSet()
        self.run = MockRun(self.workspace,self.options,self.gumpSet)
        self.cursor = MockCursor()
        self.conn = MockConnection(self.cursor)
        self.dynagumper = Dynagumper(self.run,self.conn)
    
    def tearDown(self):
        self.cleanupDatabaseMess()
        
    def testExecute(self):
        self.dynagumper._execute("blah")
        self.assertEquals( self.cursor.lastCommand, "blah" )
        # you can do anything inside a test
        # use the assertXXX methods on TestCase
        # to check conditions
        #self.assert_( True )
        #self.assertEquals( type({}), type({}) )
    
    def cleanupDatabaseMess(self):
        pass # TODO

# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(DynagumperTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
