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
    Documenter Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.core.gumprun import GumpRun
from gump.document.documenter import Documenter
from gump.document.text.documenter import TextDocumenter
from gump.document.xdocs.documenter import XDocDocumenter
from gump.stats.statsdb import *
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class DocumenterTestSuite(UnitTestSuite):
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
   
    def testText(self):
        out=StringIO.StringIO()
        documenter=TextDocumenter(self.run,out)
        documenter.document()
        out.close()
        
    def testXDocs(self):
        xtest=os.path.join(dir.test,'xdocs')
        if not os.path.exists(xtest): os.mkdir(xtest)
        documenter=XDocDocumenter(self.run,xtest,'http://someplace')
        documenter.document()
        