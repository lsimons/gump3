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
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.core.gumprun import GumpRun
from gump.test import getWorkedTestRun
from gump.runner.tasks import SequentialTaskRunner, GumpTaskList
from gump.test.pyunit import UnitTestSuite

class TasksTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
                  
      
    def suiteSetUp(self):
        #
        # Load a decent Run/Workspace
        #
        self.run=getWorkedTestRun()  
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
        
    def testBuildTasks(self):
        runner=SequentialTaskRunner(self.run)
        taskList=GumpTaskList(['build'])
        taskList.bind(runner)
        #print `taskList`
            
    def testBuildDocumentTasks(self):
        runner=SequentialTaskRunner(self.run)    
        taskList=GumpTaskList(['build','document'])
        taskList.bind(runner)
        #print `taskList`
            
    def testUpdateBuildStatsTasks(self):
        runner=SequentialTaskRunner(self.run)    
        taskList=GumpTaskList(['update','build','updateStatistics'])
        taskList.bind(runner)
        #print `taskList`