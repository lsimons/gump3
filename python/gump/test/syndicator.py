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

    Syndication Testing
    
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.core.gumprun import GumpRun
from gump.syndication.rss import RSSSyndicator
from gump.syndication.atom import AtomSyndicator
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class SyndicatorTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.run=getWorkedTestRun()
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.module1=self.workspace.getModule('module1')
        self.project1=self.workspace.getProject('project1')
        self.assertNotNone('Needed a workspace', self.workspace)
        
        
        self.rss=RSSSyndicator(self.run)
        self.atom=AtomSyndicator(self.run)
        
    def testRSSSyndicateModule(self):
        self.rss.syndicateModule(self.module1)
        
    def testAtomSyndicateModule(self):
        self.rss.syndicateModule(self.module1)
        
    def testRSSSyndicateProject(self):
        self.rss.syndicateProject(self.project1)
        
    def testAtomSyndicateProject(self):
        self.rss.syndicateProject(self.project1)
        