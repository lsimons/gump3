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
import gump.config
from gump.gumprun import GumpRun
from gump.document.documenter import Documenter
from gump.document.text.documenter import TextDocumenter
from gump.document.template.documenter import TemplateDocumenter
from gump.document.forrest.documenter import ForrestDocumenter
from gump.output.statsdb import *
from gump.test import getWorkedTestWorkspace
from gump.test.pyunit import UnitTestSuite

class DocumenterTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.workspace=getWorkedTestWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
        self.run=GumpRun(self.workspace)
        
    def testText(self):
        out=StringIO.StringIO()
        documenter=TextDocumenter(out)
        documenter.document(self.run)
        out.close()
        
    def testTemplate(self):
        out=StringIO.StringIO()
        documenter=TemplateDocumenter(out)
        documenter.document(self.run)
        out.close()
        
    def testForrest(self):
        ftest=os.path.join(dir.test,'forrest')
        if not os.path.exists(ftest): os.mkdir(ftest)
        documenter=ForrestDocumenter(ftest,'http://someplace')
        documenter.document(self.run)
        