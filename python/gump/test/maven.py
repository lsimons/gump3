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
    Maven Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.core.model.state import *
from gump.core.build.maven import generate_maven_properties, get_maven_command

import gump.core.language.java

from gump.util import *
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class MavenTestSuite(UnitTestSuite):
    """
    
        Maven Test suite
        
    """
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
        
        self.maven1=self.workspace.getProject('maven1')            
        self.assertNotNone('Needed a maven project', self.maven1)
        
        self.javaHelper=gump.core.language.java.JavaHelper(self.run)
        
    def testMavenProperties(self):
                
        self.assertTrue('Maven project has a Maven object', self.maven1.hasMaven())        
        generate_maven_properties(self.maven1, self.javaHelper, 'test/unit-testing-maven.properties')
        
    def testMavenCommand(self):                
        self.assertTrue('Maven project has a Maven object', self.maven1.hasMaven())        
  
        cmd = get_maven_command(self.maven1)
        
        # cmd.dump()
        
