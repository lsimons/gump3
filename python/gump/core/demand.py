#!/usr/bin/python


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

"""

import os.path
import sys

from gump import log
from gump.core.gumprun import *
from gump.core.runner import *
from gump.core.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *

from gump.net.cvs import *

from gump.document.text.documenter import TextDocumenter
from gump.document.forrest.documenter import ForrestDocumenter

from gump.output.statsdb import *
from gump.output.repository import JarRepository
from gump.output.nag import nag
from gump.results.resulter import gatherResults,generateResults
from gump.syndication.syndicator import syndicate


###############################################################################
# Classes
###############################################################################

class OnDemandTaskRunner(GumpRunner):

    def __init__(self,run):
        GumpRunner.__init__(self,eun)

    ###########################################
        
    def performUpdate(self):
        return self.perform(run, GumpTaskList(['update','document']) )
    
    def performBuild(self):
        return self.perform(run, GumpTaskList(['build','document']) )
    
    def performDebug(self):
        return self.perform(run, GumpTaskList(['update','build','document']) )
    
    def performIntegrate(self):
        return self.perform(run, \
                GumpTaskList(['update','build','syndicate','generateResults','document','notify']) )
        
    def performCheck(self):
        return self.perform(run, GumpTaskList(['check','document']) )
        
    ###########################################
    
    def perform(self):     
    
        # In order...
        for project in self.run.getBuildSequence():

            module=project.getModule()

            # Update on demand
            if not module.hasBeenUpdated():
                self.processModule(module)

            # Process
            self.processProject(project)

            # Keep track of progress...
            documentBuildList()

        # The wrap up...
        documentWorkspace()

    def processModule(self,module):
        
        # Update Module
        module.update()
        module.updateStats()
        module.document()
        module.syndicate()
        module.notify()
                
    def processProject(self,project):
        
        # Build project
        project.build()
        product.publishArtefacts()
        project.updateStats()
        project.document()
        project.syndicate()
        project.notify()