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

# tell Python what modules make up the gump.test package
#__all__ = ["",""]

from gump.model.loader import WorkspaceLoader

import gump
import gump.core.config

from gump.core.gumprun import *

from gump.model.state import *
from gump.model.rawmodel import XMLWorkspace
from gump.model.workspace import Workspace

from gump.stats.statsdb import StatisticsDB
from gump.utils.tools import listDirectoryToFileHolder
from gump.utils.work import *

def getTestRun(workspaceXml=None):
    workspace=getTestWorkspace(workspaceXml)
    return GumpRun(workspace,'*',getConfiguredOptions())
    
def getWorkedTestRun(workspaceXml=None):
    workspace=getWorkedTestWorkspace(workspaceXml)
    return GumpRun(workspace,'*',getConfiguredOptions())
    
def getConfiguredOptions():
    options=GumpRunOptions()
    from gump.document.xdocs.resolver import XDocResolver
    options.setResolver(XDocResolver('./test/bogus','http://bogus.org/'))
    return options

def getTestWorkspace(xml=None):
    if not xml: xml='gump/test/resources/full1/workspace.xml'    
    #print "Workspace File: " + str(xml)    
    workspace = WorkspaceLoader().load(xml)
    return workspace
    
def getWorkedTestWorkspace(xml=None):
    workspace=getTestWorkspace(xml)
       
    # Load statistics for this workspace
    db=StatisticsDB(dir.test,'test.db')  
    db.loadStatistics(workspace)

    # Some file items...
    listDirectoryToFileHolder(workspace,workspace.getBaseDirectory())        
    for module in workspace.getModules():        
        listDirectoryToFileHolder(module,module.getWorkingDirectory())
        for project in module.getProjects():
            listDirectoryToFileHolder(project,project.getHomeDirectory())  

    # Some work items...
    work=WorkItem('test',WORK_TYPE_CHECK,STATE_SUCCESS)
    workspace.getWorkList().add(work)
    for module in workspace.getModules():      
        work=WorkItem('test',WORK_TYPE_CHECK,STATE_SUCCESS)  
        module.getWorkList().add(work)
        for project in module.getProjects():
            work=WorkItem('test',WORK_TYPE_CHECK,STATE_SUCCESS)    
            project.getWorkList().add(work)     
     
    #       
    # Try to set some statii
    #
    m=0
    for module in workspace.getModules():   
        #
        # Set one in three modules as failed.
        #
        m+=1 
        if m % 3 == 0:
            module.changeState(STATE_FAILED)
        else:
            if m % 2 == 0:
                module.setModified(1)
            module.changeState(STATE_SUCCESS)
        p=0
        for project in module.getProjects(): 
            #
            # Set one in three projects as failed.
            #
            p+=1
            if p % 3 == 0:
                project.changeState(STATE_FAILED)
            else:
                project.changeState(STATE_SUCCESS)

    return workspace
    
def createTestWorkspace():
    xmlworkspace=XMLWorkspace({})
    workspace=Workspace(xmlworkspace)
    return workspace
  
    