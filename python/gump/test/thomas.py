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
from gump.core.engine import GumpTask, GumpTaskList, GumpEngine
from gump.test.pyunit import UnitTestSuite

class EngineTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
            
    def testBuildTasks(self):
        engine=GumpEngine()
        taskList=GumpTaskList(['build'])
        taskList.bind(engine)
        #print `taskList`
            
    def testBuildDocumentTasks(self):
        engine=GumpEngine()    
        taskList=GumpTaskList(['build','document'])
        taskList.bind(engine)
        #print `taskList`
            
    def testUpdateBuildStatsTasks(self):
        engine=GumpEngine()    
        taskList=GumpTaskList(['update','build','updateStatistics'])
        taskList.bind(engine)
        #print `taskList`