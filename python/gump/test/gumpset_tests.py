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
    GumpSet Testing
"""

import os
import logging

from gump import log
import gump.config
from gump.model.loader import WorkspaceLoader
from gump.engine import GumpSet

def testWorkspace(file):
print "Workspace File: " + str(file)
   
   ws = WorkspaceLoader().load(file)
   
   print "Projects in Workspace:" + str(len(ws.getProjects()))
   print "Modules in Workspace:" + str(len(ws.getModules()))
   
   ws.dump()
   
   gumpSet=GumpSet(ws)
   
   # Get/displaythe projects
   projects=gumpSet.getProjects()
   print "Projects:" + str(len(projects))
   for p in projects:
       print " Project : " + p.getName()
       
   sequence=gumpSet.getProjectSequence()   
   print "Project Sequence:" + str(len(sequence))
   for p in sequence:
       print " Sequence: " + p.getName()

   gumpSet.dump()

if __name__=='__main__':

    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)

    #testWorkspace('gump/test/resources/simple1/standalone_workspace.xml')
    testWorkspace('gump/test/resources/full1/workspace.xml')

