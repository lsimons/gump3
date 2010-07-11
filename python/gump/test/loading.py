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

    WorkspaceLoading Testing
    
"""

import os
import logging
import types, StringIO

from gump import log
from gump.core.loader.loader import *

from gump.util import *
from gump.test.pyunit import UnitTestSuite

class LoadingTestSuite(UnitTestSuite):
    """
    
        Loader Test suite
        
    """
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def performLoad(self,file):
        return WorkspaceLoader(True).load(file)

    def testSimple1(self):
        self.performLoad('gump/test/resources/simple1/standalone_workspace.xml')
        
    def testSimple2(self):
        self.performLoad('gump/test/resources/simple2/workspace.xml')
        
    def testFull1(self):
        self.performLoad('gump/test/resources/full1/workspace.xml')
        
    def testBroken1(self):
        self.performLoad('gump/test/resources/broken1/broken_workspace.xml')
        
    # :TODO: Need to fix
    #def testCircular1(self):
    #    self.performLoad('gump/test/resources/circular1/workspace.xml')
        
