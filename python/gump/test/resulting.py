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

from gump import log
import gump.core.config
from gump.core.run.gumprun import GumpRun
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite
from gump.core.model.state import *
from gump.actor.results.model import *
from gump.actor.results.resulter import generateResults,Resulter
from gump.actor.results.loader import WorkspaceResultLoader
from gump.util.smtp import *

class ResultingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
        self.testFile = 'test/test.xml'
        
            
    def suiteSetUp(self):
        #
        # Load a decent Run/Workspace
        #
        self.run=getWorkedTestRun()  
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
    
    def checkWorkspaceResult(self,wsr):
        self.assertTrue('Has some ModuleResults', wsr.hasModuleResults())
        self.assertTrue('Has some ProjectResults', wsr.hasProjectResults())
        
        for moduleResult in wsr.getModuleResults():
            self.assertTrue('Has some ProjectResults', moduleResult.hasProjectResults())
            
    def testResultContents(self):
    
        resulter=Resulter(self.run)
        
        # Construct from run
        wsr = resulter.constructResults()
        
        # Check out these results
        self.checkWorkspaceResult(wsr)
        
    def testResultWrite(self):
    
        resulter=Resulter(self.run)
        
        # Write to file...
        resulter.generateResults(self.testFile)   
        
        self.assertTrue('Wrote a file', os.path.exists(self.testFile))       
        
    def testResultRead(self):
    
        resulter=Resulter(self.run)

        # Write to file...
        resulter.generateResults(self.testFile)        
        
        # Read the file...      
        wsr = resulter.loadResults(self.testFile)
        
        self.checkWorkspaceResult(wsr)
                
        #wsr.dump()
        
    def testServers(self):
    
        resulter=Resulter(self.run)

        # Load for all servers...
        resulter.loadResultsForServers()        
        
    def testNoDifferences(self):
        r=ResultsSet()
        
        m1= ResultModelObject('a')
        r['a']=m1
        
        m2= ResultModelObject('b')
        r['b']=m2
        
        self.assertFalse('No Differences', r.hasDifferences())
              
    def testDifferences(self):
        r=ResultsSet()
        
        m1= ResultModelObject('a')
        m1.setStatePair(StatePair(STATE_SUCCESS,REASON_UNSET))
        r['a']=m1
        
        m2= ResultModelObject('b')
        r['b']=m2
        
        self.assertTrue('Differences', r.hasDifferences())
              
    def testContainsNoFailure(self):
        r=ResultsSet()
        
        m1= ResultModelObject('a')
        m1.setStatePair(StatePair(STATE_SUCCESS,REASON_UNSET))
        r['a']=m1
        
        m2= ResultModelObject('b')
        m2.setStatePair(StatePair(STATE_SUCCESS,REASON_UNSET))
        r['b']=m2
        
        self.assertFalse('No Failure', r.containsFailure())
              
    def testContainsFailure(self):
        r=ResultsSet()
        
        m1= ResultModelObject('a')
        m1.setStatePair(StatePair(STATE_FAILED,REASON_UNSET))
        r['a']=m1
        
        m2= ResultModelObject('b')
        m2.setStatePair(StatePair(STATE_SUCCESS,REASON_UNSET))
        r['b']=m2
        
        self.assertTrue('Failure', r.containsFailure())
        
