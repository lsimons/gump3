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

    Syndication Testing
    
"""

import os
import logging
import types, io

from gump import log
import gump.core.config
from gump.core.run.gumprun import GumpRun
from gump.actor.rdf.describer import RDFDescriber
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class RDFDescriberTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.run=getWorkedTestRun()
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.project1=self.workspace.getProject('project1')
        self.project2=self.workspace.getProject('project2')
        self.project3=self.workspace.getProject('project3')
        self.assertNotNone('Needed a workspace', self.workspace)
        
        self.rdf=RDFDescriber(self.run)        
        
    def testDescribeProject(self):
        self.rdf.describeProject(self.project1)        
        
    def testDescribeWorkspace(self):
        
        # Populate some proejcts (side effects)
        self.rdf.describeProject(self.project1)        
        self.rdf.describeProject(self.project2)    
        self.rdf.describeProject(self.project3)
        # Do the worksapce w/ those 3 above, plus repos, etc.    
        self.rdf.describeWorkspace()
        
        
