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
    Maven Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.model.state import *
from gump.model.loader import WorkspaceLoader
from gump.utils import *
from gump.test import getWorkedTestWorkspace
from gump.test.pyunit import UnitTestSuite

class MavenTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.workspace=getWorkedTestWorkspace() 
         
        self.assertNotNone('Needed a workspace', self.workspace)            
        self.maven1=self.workspace.getProject('maven1')            
        
        
    def testMavenProperties(self):
                
        self.assertTrue('Maven project has a Maven object', self.maven1.hasMaven())
        
        self.maven1.generateMavenProperties('test/unit-testing-maven.properties')
        
        cmd=self.maven1.getMavenCommand()
        
        # cmd.dump()
        