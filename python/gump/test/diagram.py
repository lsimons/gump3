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
    Drawing Testing
"""

from gump import log
from gump.svg.drawing import *
from gump.svg.scale import ScaleDiagram
from gump.svg.depdiag import DependencyDiagram
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

import StringIO

class DiagramTestSuite(UnitTestSuite):
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
        
        
        self.project5=self.workspace.getProject('project5')
        
    def testDependencyDiagramGeneration(self):
        diagram=DependencyDiagram(self.project5)        
        diagram.compute()        
        svg=diagram.generateDiagram()
        svg.serializeToFile('x.svg')
        
    def testScaleDiagramGeneration(self):
        diagram=ScaleDiagram([10,20])                
        svg=diagram.generateDiagram()
        stream=StringIO.StringIO() 
        svg.serialize(stream)
        stream.close()
        
        