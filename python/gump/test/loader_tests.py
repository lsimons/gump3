#!/usr/bin/env python
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
    Loader Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.model.loader import WorkspaceLoader
from gump.utils import *
from gump.utils.xmlutils import xmlize
from gump.test import *

def testWorkspace(url):
   print "Workspace URL: " + str(url)
   return WorkspaceLoader().load(url)

def testModule(url,ws):
   print "Workspace URL: " + str(url)
   return WorkspaceLoader().loadModule(url,ws)

if __name__=='__main__':

    gumpinit()

    #:TODO: Do a loop over directories and load all?
    
    #testWorkspace('gump/test/resources/simple1/standalone_workspace.xml').dump() 

    #testWorkspace('gump/test/resources/simple2/workspace.xml').dump()
    
    testWorkspace('gump/test/resources/full1/workspace.xml').dump()

    #try:
    #    testWorkspace('gump/test/resources/broken1/broken_workspace.xml') 
    #except:
    #    print "Fixme" # :TODO: Just set status on bad sub-elements, not fail whole
    #    
    #ws = createTestWorkspace()
    
    #module=testModule('http://cvs.apache.org/viewcvs.cgi/*checkout*/avalon/buildsystem/gump-integration/project/avalon.xml',ws)
    
    #dump(module)
    
    #printSeparator()
    #print xmlize('module', module, ws)
  
