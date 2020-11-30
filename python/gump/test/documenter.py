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
    Documenter Testing
"""

import os
import logging
import types, io

from gump import log
import gump.core.config
from gump.core.run.gumprun import GumpRun
from gump.actor.document.documenter import Documenter
from gump.actor.document.text.documenter import TextDocumenter
from gump.actor.document.xdocs.documenter import XDocDocumenter
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
        out=io.StringIO()
        documenter=TextDocumenter(self.run,out)
        documenter.document()
        out.close()
        
    def testXDocs(self):
        xtest=os.path.join(gump.core.config.dir.test,'xdocs')
        if not os.path.exists(xtest): os.mkdir(xtest)
        documenter=XDocDocumenter(self.run,xtest,'http://someplace')
        documenter.document()
        
