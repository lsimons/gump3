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
    Statistics Testing
"""

import os
import logging
import types, io

from gump import log
import gump.core.config
from gump.actor.stats.dbm.statsdb import StatisticsDB
from gump.actor.stats.statistician import Statistician
from gump.util import *
from gump.util.timing import *
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class StatsTestSuite(UnitTestSuite):
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
        self.project1=self.workspace.getProject('project1')        
        self.module1=self.workspace.getModule('module1')
    
        self.statsDB=StatisticsDB(gump.core.config.dir.test,'test.db')
        self.stats=Statistician(self.run,self.statsDB)
        
    def testGetStats(self):
        self.statsDB.getProjectStats(self.project1.getName())
        self.statsDB.getModuleStats(self.module1.getName())
        self.statsDB.getRepositoryStats(self.repo1.getName())
        
        
    def testPutStats(self):
        ps1=self.statsDB.getProjectStats(self.project1.getName())
        ms1=self.statsDB.getModuleStats(self.module1.getName())
        rs1=self.statsDB.getRepositoryStats(self.repo1.getName())
                
        self.statsDB.putProjectStats(ps1)
        self.statsDB.putModuleStats(ms1)
        self.statsDB.putRepositoryStats(rs1)
              
    def testGetChangePutGetCheckStats(self):
        # Get 1
        ps1=self.statsDB.getProjectStats(self.project1.getName())
        ms1=self.statsDB.getModuleStats(self.module1.getName())
        rs1=self.statsDB.getRepositoryStats(self.repo1.getName())
                
        # Change
        ps1s = ps1.successes
        ps1.successes += 1
        
        ps1f = ps1.failures
        ps1.failures += 1
        
        ps1p = ps1.prereqs
        ps1.prereqs += 1
        
        ps1seq = ps1.sequenceInState
        ps1.sequenceInState += 1
        
        # Put        
        self.statsDB.putProjectStats(ps1)
        self.statsDB.putModuleStats(ms1)
        self.statsDB.putRepositoryStats(rs1)
        
        # Get 2
        ps2=self.statsDB.getProjectStats(self.project1.getName())
        ms2=self.statsDB.getModuleStats(self.module1.getName())
        rs2=self.statsDB.getRepositoryStats(self.repo1.getName())
            
        if not os.name == 'dos' and not os.name == 'nt':  
            self.assertGreater('Incremented Successes', ps2.successes, ps1s )
            self.assertGreater('Incremented Failures', ps2.failures, ps1f )
            self.assertGreater('Incremented Prereqs', ps2.prereqs, ps1p )
            self.assertGreater('Incremented SequenceInState', ps2.sequenceInState, ps1seq )
        
        #print str(ps1s) + ' : ' + str(ps1f) + ' : ' + str(ps1p) + ' : ' + str(ps1seq)
        
        self.statsDB.sync()
        
    def testLoadAndUpdateStats(self):
        self.stats.loadStatistics()
        
        # Mark Modified (so we get an Modified reading)
        self.module1.setModified(True)
        
        self.stats.updateStatistics()   
        
        lastModified=self.module1.getLastModified()
        
        # Give some padding.
        lastModified -= datetime.timedelta(seconds=60*60*7)
        
        rough=getGeneralDifferenceDescription(default.datetime, lastModified)
        self.assertNonZeroString('Date Diff String', rough)
        self.assertNotSubstring('Date Diff String', 'year', rough)        
     
        
