#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Updater Testing
"""

import os
import logging
import types, io

from gump import log
import gump.core.config
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

from gump.core.update.updater import GumpUpdater

class UpdaterTestSuite(UnitTestSuite):
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
   
        self.repo1=self.workspace.getRepository('repository1')                  
        self.svnRepo1=self.workspace.getRepository('svn_repository1')                  
        
        self.module1=self.workspace.getModule('module1')      
        self.svnModule1=self.workspace.getModule('svn_module1')
        self.downloadModule1=self.workspace.getModule('download1')
        
        self.update=GumpUpdater(self.run)
            
    def testCommandLines(self):
        
        # Hmm, need to test checkouts and updates and status...
        # but how, since we now delegate more    
        
        pass
